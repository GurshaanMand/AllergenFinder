#ADD: when retrieving from api if smt happens and i need to restart i only want to re retrieve things i havent previouslyt retrieved
import sqlite3
import requests
import json

conn = sqlite3.connect('allergen.sqlite')
curr = conn.cursor()

def interFace():
    all = userInput("", "")

    searchDB(all[0])



def userInput(recipe, allergy):
    recipe = input("Enter the food you want to check for allergens: ")
    l = list()

    while(True):
        allergy = input("Enter the Allergy you want to check for, type 'done' when finished: ").lower()
        if allergy == "done":
            break
        l.append(allergy)
    # print("List of your allergies to watch out for: ", l)
    all = list()
    all.append(recipe)
    all.append(l)

    return all

def searchDB(recipe):
    curr.execute("SELECT EXISTS(SELECT 1 FROM Recipe WHERE name = ?)", (recipe.lower(),))
    exists = curr.fetchone()[0] #EXISTS return 1 if at least one row exists otherwise 0


    if exists == 1:
        #recipe name exists
        curr.execute("SELECT allergens FROM Recipe WHERE name = ?", (recipe.lower(),))
        row = curr.fetchone()[0]
        listAllergies = json.loads(row)
        print("Allergen in ", recipe, ": ", listAllergies)
    elif exists == 0:
        #recipe name does not exist
        #-If the name of the recipe is not in the database then send the api request for that recipe
        print("Sending request to database...")
        runAPI(recipe)
        return
    else:
        print("Something went wrong")


    


def runAPI(recipe):
    api_key = "*******"
    url = "https://api.spoonacular.com/recipes/complexSearch"


    params = {
        "query": (recipe.lower()),
        "number": 5,
        "offset": 0,
        "apiKey": api_key
    }

    try:
        d = requests.get(url, params=params)
    except:
        print("Something went wrong, try again.")

    data = d.json() #data variable is json
    

    if (data["totalResults"]) == 0:
        print("Couldn't find your item ", recipe, " in database")
    else:
        allAllergies = ["dairy", "egg", "gluten", "grain", "peanut", "seafood", "sesame", "shellfish", "soy", "sulfite", "tree nut", "wheat", "cheese"]

        for i in data["results"]:
            id  = i["id"]
            name = i["title"].lower()
            

            url = "https://api.spoonacular.com/recipes/" + str(id) + "/information?includeNutrition=false&addWinePairing=false&addTasteData=false"

            params = {
            "apiKey": api_key
            }

            try:
                m = requests.get(url ,params=params)
            except Exception as e:
                print("Request failed:", e)

            m = m.json()

            ingre = m.get("extendedIngredients", [])

            foundAllergies = list()

            for j in ingre:
                nam = j.get("name","").lower()
                aisle = j.get("aisle","").lower()
                for allergen in allAllergies:
                    if allergen in nam or allergen in aisle:
                        if allergen not in foundAllergies:
                            foundAllergies.append(allergen)
                        
            #remove duplicates in allergens
            #Basically removing duplicate parts of a string
            jString = json.dumps(foundAllergies) 

            print(id, name, jString)
            curr.execute("INSERT OR IGNORE INTO Recipe (id, name, allergens) VALUES (?,?, ?)", (id, name, jString))
            conn.commit()

    searchDB(recipe)
interFace()