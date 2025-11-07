import os
import json

def load_recipes(data_folder='data'):
    all_recipes = []
    for filename in os.listdir(data_folder):
        if filename.endswith('.json'):
            filepath = os.path.join(data_folder, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                cuisine = data.get("cuisine", "Unknown")
                for recipe in data.get("recipes", []):
                    recipe['cuisine'] = cuisine  # ensure cuisine field is present
                    all_recipes.append(recipe)
    return all_recipes

# Test the loader
if __name__ == "__main__":
    recipes = load_recipes()
    print(f"Total recipes loaded: {len(recipes)}")
    print("Sample recipe:", recipes[0])
