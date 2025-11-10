from src.data_loader import load_recipes
from src.matching import match_recipes

recipes = load_recipes()
cuisine = "American"
course = "Dessert"
user_ings = ["sugar", "cocoa powder"]

# Filter recipes for the cuisine & course and print them
subset = [r for r in recipes if r.get('cuisine','').strip().lower()==cuisine.lower() and r.get('course','').strip().lower()==course.lower()]
print("Found", len(subset), "recipes for", cuisine, "/", course)
for r in subset:
    print(" -", r['name'], "| ingredients:", r['ingredients'])

print("\nRunning matcher...")
matches = match_recipes(user_ings, subset, course=course, cuisine=cuisine)
if not matches:
    print("No matches returned by match_recipes().")
else:
    for m in matches[:10]:
        print("Score:", m['score'], "|", m['recipe']['name'], "| ingredients:", m['recipe']['ingredients'])
