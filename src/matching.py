def normalize_ingredient(ing):
    """
    Normalize ingredient:
    - lowercase
    - strip spaces
    - simple plural handling: remove trailing s/es
    """
    ing = ing.strip().lower()
    if ing.endswith('es'):
        ing = ing[:-2]
    elif ing.endswith('s'):
        ing = ing[:-1]
    return ing

def match_recipes(user_ingredients, recipes_list, course=None, cuisine=None):
    """
    Match recipes based on user ingredients, optional course and cuisine.
    Handles plurals and simple ingredient normalization.
    
    Args:
        user_ingredients (list of str): Ingredients provided by user
        recipes_list (list of dict): List of recipes
        course (str, optional): Course filter
        cuisine (str, optional): Cuisine filter
    
    Returns:
        list of dict: Matched recipes sorted by relevance
    """
    user_ingredients = [normalize_ingredient(i) for i in user_ingredients]
    matched_recipes = []

    for recipe in recipes_list:
        # Filter by course
        if course and recipe['course'].strip().lower() != course.strip().lower():
            continue
        # Filter by cuisine
        if cuisine and recipe['cuisine'].strip().lower() != cuisine.strip().lower():
            continue

        # Normalize recipe ingredients
        recipe_ings = [normalize_ingredient(i) for i in recipe['ingredients']]

        # Count matching ingredients
        match_count = sum(1 for i in user_ingredients if i in recipe_ings)

        if match_count > 0:
            matched_recipes.append({'recipe': recipe, 'score': match_count})

    # Sort: most matched ingredients first, then by fewer total ingredients
    matched_recipes.sort(key=lambda x: (-x['score'], len(x['recipe']['ingredients'])))
    return matched_recipes
