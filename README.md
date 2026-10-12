# AllergenFinder

A command-line tool that looks up the likely allergens in a dish. It gets a recipe's ingredients from the [Spoonacular API](https://spoonacular.com/food-api), matches them against a list of common allergens, and stores the result in a local SQLite database.

This is not a substitute for reading a real ingredient label. The matching is keyword-based and will miss things.

## How It Works

1. You enter the name of a dish.
2. `allergenFinder.py` looks for an exact name match in the `Recipe` table of `allergen.sqlite`. If it finds one, it prints the stored allergens.
3. If not, it searches Spoonacular for up to five matching recipes and fetches each recipe's ingredient list.
4. Each ingredient's name and grocery aisle are checked for 13 allergen keywords: dairy, egg, gluten, grain, peanut, seafood, sesame, shellfish, soy, sulfite, tree nut, wheat, and cheese.
5. The recipe and its allergens (as a JSON list) are inserted into SQLite, and the lookup runs again against the database.

`addToDatabase.py` is a separate script that seeds the database from a hard-coded search query. The included `allergen.sqlite` already holds 43 recipes.

## Tech Stack

Python · SQLite · Spoonacular REST API · requests · RapidFuzz

## Run It

```bash
pip install requests rapidfuzz
python allergenFinder.py
```

You need your own Spoonacular API key. Replace the `api_key` placeholder in `allergenFinder.py` (and in `addToDatabase.py` if you use it).

## Known Issues

- When a dish has no exact match, the script tries to suggest a close match by category using RapidFuzz. That step reads a `category` column the current table does not have, so it fails before reaching the API search.
- The prompt collects the allergies you care about, but the output lists every allergen found; it is not filtered to your list yet.
- Matching is by substring, so an ingredient is only caught if its name or aisle contains one of the keywords.
