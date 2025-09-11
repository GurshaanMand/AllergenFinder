import sqlite3
import requests
import json


conn = sqlite3.connect('allergen.sqlite')
curr = conn.cursor()

api_key = "*********"
url = "https://api.spoonacular.com/recipes/complexSearch"


params = {
    "query": "chicken",
    "number": 20,
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
# print("Total Results:", data["totalResults"])

list = ["dairy", "egg", "gluten", "grain", "peanut", "seafood", "sesame", "shellfish", "soy", "sulfite", "tree nut", "wheat", "cheese"]

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

    allergens = ""

    for j in ingre:
        nam = j["name"].lower()
        aisle = j["aisle"].lower()
        for allergen in list:
            if allergen in nam or allergen in aisle:
                allergens += allergen + " "

    print(id, name, allergens)
    curr.execute("INSERT OR IGNORE INTO Recipe (id, name, allergens) VALUES (?,?, ?)", (id, name, allergens))

conn.commit()
