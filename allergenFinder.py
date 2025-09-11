import sqlite3
import urllib.request, urllib.parse, urllib.error
import json


conn = sqlite3.connect('allergen.sqlite')
curr = conn.cursor()

try:
    url = "https://world.openfoodfacts.org/api/v0/product/737628064502.json"
except:
    print("Something went wrong, try again.")

curr.executescript(""" 
DROP TABLE IF EXISTS Allergen;
            
CREATE TABLE Allergen(
    id  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    ingredient    TEXT UNIQUE
)
""")

uh = urllib.request.urlopen(url)
data = uh.read().decode()

# {
#   "status": 1,
#   "product": {
#     "product_name": "Organic Almond Milk",
#     "brands": "Silk",
#     "ingredients_text": "Filtered water, almonds, cane sugar, ..."
#     // Additional product information
#   }
# }
print(data)
# for i in data:
#     print(i)

