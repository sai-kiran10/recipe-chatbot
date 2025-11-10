from src.data_loader import load_recipes

recipes = load_recipes()
print("Total recipes loaded:", len(recipes))
# Show sample of a few recipes for each cuisine
from collections import defaultdict
by_cuisine = defaultdict(list)
for r in recipes:
    by_cuisine[r.get('cuisine','Unknown')].append(r)

for c, lst in by_cuisine.items():
    print("\nCuisine:", repr(c), "| count:", len(lst))
    for r in lst[:3]:
        print(" - name:", repr(r.get('name')))
        print("   course:", repr(r.get('course')))
        print("   ingredients:", r.get('ingredients'))
