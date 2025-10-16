import sqlite3
import requests
import json


conn = sqlite3.connect('allergen.sqlite')
curr = conn.cursor()

api_key = "*********"
url = "https://api.spoonacular.com/recipes/complexSearch"


params = {
    "query": "poutine",
    "number": 1,
    "offset": 0,
    "apiKey": api_key
}

try:
    d = requests.get(url, params=params)
except:
    print("Something went wrong, try again.")

curr.executescript(""" 
                   
CREATE TABLE IF NOT EXISTS Recipe(
    id        INTEGER NOT NULL PRIMARY KEY,
    name      TEXT UNIQUE,
    allergens  TEXT
)
             
""")

data = d.json()
print("Total Results:", data["totalResults"])

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
    except:
        print("Something went wrong, try again.")

    m = m.json()

    ingre = m.get("extendedIngredients", [])
    # lst = ingredients.rstrip().lower().split()

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
