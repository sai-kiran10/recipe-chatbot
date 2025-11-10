import re
from src.data_loader import load_recipes
from src.matching import match_recipes, normalize, tokenize, words_match
# If your matching.py doesn't expose normalize/tokenize/words_match, paste their logic here similarly.

recipes = load_recipes()
cuisine = "American"
course = "Dessert"
user_ings = ["sugar", "cocoa powder"]

subset = [r for r in recipes if r.get('cuisine','').strip().lower()==cuisine.lower() and r.get('course','').strip().lower()==course.lower()]
print("Candidates:", len(subset))

for r in subset:
    print("\nRecipe:", r['name'])
    recipe_ings = r.get('ingredients', [])
    print(" recipe ingredients raw:", recipe_ings)
    matches = []
    for ui in user_ings:
        matched = []
        for ri in recipe_ings:
            # try simple lowercase containment first
            if ui.strip().lower() in ri.strip().lower() or ri.strip().lower() in ui.strip().lower():
                matched.append(ri)
            else:
                # fallback: token overlap
                utoks = set(re.sub(r'[^\w\s]','',ui.lower()).split())
                rtoks = set(re.sub(r'[^\w\s]','',ri.lower()).split())
                if utoks & rtoks:
                    matched.append(ri)
        print(" user ingredient:", ui, "-> matched recipe ingredients:", matched)
        if matched:
            matches.append((ui, matched))
    print("Total matched user ingredients count:", len(matches))
