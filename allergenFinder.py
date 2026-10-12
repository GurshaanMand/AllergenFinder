import sqlite3
import requests
import json
from rapidfuzz import process, fuzz

conn = sqlite3.connect('allergen.sqlite')
curr = conn.cursor()


def interFace():
    all = userInput("", "")

    searchDB(all[0])


def userInput(recipe, allergy):
    recipe = input("Enter the food you want to check for allergens: ").lower()
    l = list()

    while (True):
        allergy = input(
            "Enter the Allergy you want to check for, type 'done' when finished: ").lower()
        if allergy == "done":
            break
        l.append(allergy)
    # print("List of your allergies to watch out for: ", l)
    all = list()
    all.append(recipe)
    all.append(l)

    return all


def searchDB(recipe):
    curr.execute("SELECT EXISTS(SELECT 1 FROM Recipe WHERE name = ?)", (recipe,))
    exists = curr.fetchone()[0]  # EXISTS return 1 if at least one row exists otherwise 0

    if exists == 1:
        # recipe name exists
        curr.execute("SELECT allergens FROM Recipe WHERE name = ?", (recipe,))
        row = curr.fetchone()[0]
        listAllergies = json.loads(row)
        print("Allergen in ", recipe, ": ", listAllergies)
    elif exists == 0:
        # recipe name does not exist
        # use rapidfuzz to suggest the closest stored recipe before calling the API
        curr.execute("SELECT name FROM Recipe")
        all_names = [r[0] for r in curr.fetchall()]
        match = process.extractOne(recipe, all_names, scorer=fuzz.WRatio) if all_names else None

        if match and match[1] > 60:  # Get a potential recipe match
            print("Did you mean: ", match[0])
            confirm = input("Enter Y to confirm, N to search online: ").lower()

            if confirm == "y":
                curr.execute("SELECT allergens FROM Recipe WHERE name = ?", (match[0],))
                row = curr.fetchone()
                print(f"Allergens in {match[0]}: {row[0]}")
                return

        # No close match, or the suggestion was rejected: send API request
        print("Sending request to database...")
        runAPI(recipe)
        return
    else:
        print("Something went wrong")


def runAPI(recipe):
    api_key = "*******"
    url = "https://api.spoonacular.com/recipes/complexSearch"

    params = {
        "query": (recipe),
        "number": 5,
        "offset": 0,
        "apiKey": api_key
    }

    try:
        d = requests.get(url, params=params)
    except:
        print("Something went wrong, try again.")

    data = d.json()  # data variable is json

    print(data)

    if data.get("status") == "failure":
        print("Message:", data.get("message", "Unknown error"))
        return

    if not data.get("results"):
        print("No results found for", recipe)
        return

    if (data["totalResults"]) == 0:
        print("Couldn't find your item ", recipe, " in database")
    else:
        allAllergies = ["dairy", "egg", "gluten", "grain", "peanut", "seafood",
                        "sesame", "shellfish", "soy", "sulfite", "tree nut", "wheat", "cheese"]
        inserted = False
        for i in data["results"]:
            id = i["id"]
            name = i["title"].lower()

            # Skip if already exists
            curr.execute("SELECT 1 FROM Recipe WHERE id = ?", (id,))
            if curr.fetchone():
                print(f"Skipping existing recipe: {name}")
                continue

            url = "https://api.spoonacular.com/recipes/" + \
                str(id) + "/information?includeNutrition=false&addWinePairing=false&addTasteData=false"

            params = {
                "apiKey": api_key
            }

            try:
                m = requests.get(url, params=params)
            except Exception as e:
                print("Request failed:", e)

            m = m.json()

            ingre = m.get("extendedIngredients", [])

            foundAllergies = list()

            for j in ingre:
                nam = j.get("name", "").lower()
                aisle = j.get("aisle", "").lower()
                for allergen in allAllergies:
                    if allergen in nam or allergen in aisle:
                        if allergen not in foundAllergies:
                            foundAllergies.append(allergen)

            # remove duplicates in allergens
            # Basically removing duplicate parts of a string
            jString = json.dumps(foundAllergies)

            print(id, name, jString)
            curr.execute(
                "INSERT OR IGNORE INTO Recipe (id, name, allergens) VALUES (?,?, ?)", (id, name, jString))
            conn.commit()
            inserted = True
            print(f"✅ Added {name} with allergens {foundAllergies}")

        # only recheck if something was successfully inserted
        if inserted:
            print("Checking database for your recipe again...")
            searchDB(recipe)
        else:
            print("No new data inserted; skipping recheck.")


interFace()
