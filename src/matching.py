import re
from difflib import SequenceMatcher

def normalize(text):
    """Lowercase, strip spaces, remove punctuation."""
    return re.sub(r'[^\w\s]', '', text.lower().strip())

def tokenize(text):
    """Split text into normalized tokens."""
    return normalize(text).split()

def singularize(word):
    """Very basic singularization for common plurals."""
    if word.endswith("ies"):
        return word[:-3] + "y"
    elif word.endswith("oes"):
        return word[:-2]
    elif word.endswith("es") and len(word) > 3:
        return word[:-2]
    elif word.endswith("s") and len(word) > 3:
        return word[:-1]
    return word

def words_match(w1, w2, threshold=0.8):
    """Check if two words match, considering singular/plural and fuzzy match."""
    w1, w2 = singularize(w1), singularize(w2)
    ratio = SequenceMatcher(None, w1, w2).ratio()
    return ratio >= threshold or w1 in w2 or w2 in w1

def match_recipes(user_ingredients, recipes_list, course=None, cuisine=None):
    """
    Robust recipe matcher that handles plurals, partials, and fuzzy matches.
    """
    user_tokens_list = [tokenize(ing) for ing in user_ingredients]
    matched_recipes = []

    for recipe in recipes_list:
        if course and recipe.get('course', '').strip().lower() != course.strip().lower():
            continue
        if cuisine and recipe.get('cuisine', '').strip().lower() != cuisine.strip().lower():
            continue

        recipe_tokens_list = [tokenize(ing) for ing in recipe.get('ingredients', [])]
        match_count = 0

        for u_tokens in user_tokens_list:
            for r_tokens in recipe_tokens_list:
                if any(words_match(u, r) for u in u_tokens for r in r_tokens):
                    match_count += 1
                    break

        if match_count > 0:
            matched_recipes.append({'recipe': recipe, 'score': match_count})

    matched_recipes.sort(key=lambda x: (-x['score'], len(x['recipe'].get('ingredients', []))))
    return matched_recipes
