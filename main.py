import streamlit as st
from src.data_loader import load_recipes
from src.matching import match_recipes
import re

# Load recipes once
recipes = load_recipes()

st.set_page_config(page_title="Recipe Chatbot", page_icon="🍳")
st.title("🍳 Recipe Chatbot")

# Reset conversation button
if st.button("🔄 Reset Conversation"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]

st.write("Hi! I can suggest recipes based on your cuisine, course, and ingredients.")

# Initialize session state
if "step" not in st.session_state:
    st.session_state.step = 1
if "cuisine" not in st.session_state:
    st.session_state.cuisine = ""
if "course" not in st.session_state:
    st.session_state.course = ""
if "ingredients" not in st.session_state:
    st.session_state.ingredients = ""
if "follow_up" not in st.session_state:
    st.session_state.follow_up = []

# Helper function to handle follow-ups
def process_follow_up(text, ingredients, current_filters):
    text = text.lower()
    # Add new ingredients mentioned
    new_ings = re.findall(r'\b\w+\b', text)
    ingredients += [i for i in new_ings if i not in ingredients]
    # Dietary filters
    if "vegan" in text:
        current_filters['type_filter'] = "Vegan"
    elif "vegetarian" in text:
        current_filters['type_filter'] = "Vegetarian"
    elif "non-veg" in text or "non vegetarian" in text:
        current_filters['type_filter'] = "Non-Vegetarian"
    # Healthy filter
    if "healthy" in text or "low calorie" in text:
        current_filters['healthy_only'] = True
    # Max calories
    match = re.search(r'under (\d+)', text)
    if match:
        current_filters['max_calories'] = int(match.group(1))
    # Course change
    courses = ["breakfast", "lunch", "dinner", "snack", "dessert"]
    for c in courses:
        if c in text:
            current_filters['course'] = c.capitalize()
    return ingredients, current_filters

# Step 1: Select Cuisine
if st.session_state.step == 1:
    cuisines = sorted(list(set([r['cuisine'] for r in recipes])))
    
    # Use st.session_state.cuisine directly as the value holder
    st.session_state.cuisine = st.selectbox(
        "Select a cuisine:", 
        cuisines, 
        key="cuisine_select" # Give it a unique, explicit key
    )
    
    if st.button("Next"):
        # GUARDIAN LOGIC: ONLY advance step upon button click
        st.session_state.step = 2

# Step 2: Select Course
elif st.session_state.step == 2:
    # Filter recipes by selected cuisine
    cuisine_recipes = [
        r for r in recipes
        if r.get("cuisine", "").strip().lower() == st.session_state.cuisine.strip().lower()
    ]
    courses = sorted(list(set([r["course"].strip() for r in cuisine_recipes])))

    # Temporary variable to hold user selection
    selected_course = st.selectbox(
        "Select a course:",
        courses,
        key="course_select"
    )

    # Wait for user confirmation before updating session state
    if st.button("Next"):
        st.session_state.course = selected_course
        st.session_state.step = 3

# Step 3: Enter Ingredients
elif st.session_state.step == 3:
    ingredients_input = st.text_input(
        "Enter ingredients you have (comma separated):",
        placeholder="e.g., rice, tomato, carrot"
    )
    if st.button("Find Recipes"):
        if not ingredients_input:
            st.warning("Please enter at least one ingredient.")
        else:
            st.session_state.ingredients = ingredients_input
            st.session_state.step = 4

# Step 4: Show Recipe Suggestions + Follow-ups
elif st.session_state.step == 4:
    user_ingredients = [i.strip() for i in st.session_state.ingredients.split(",") if i.strip()]

    # Normalize cuisine
    sel_cuisine = st.session_state.cuisine.strip().lower()
    sel_course = st.session_state.course.strip().lower()

    # Candidates for selected cuisine + course
    cuisine_recipes = [
        r for r in recipes
        if r.get("cuisine", "").strip().lower() == sel_cuisine
    ]
    course_candidates = [
        r for r in cuisine_recipes
        if r.get("course", "").strip().lower() == sel_course
    ]

    # Match recipes
    matched = match_recipes(user_ingredients, course_candidates, course=st.session_state.course, cuisine=st.session_state.cuisine)

    st.markdown("## 🍽️ Recipe Suggestions")
    if not matched:
        st.info("No matching recipes found. Try different ingredients!")
    else:
        st.success(f"Top {len(matched)} recipe(s) for you:")
        for item in matched:
            r = item["recipe"]
            st.markdown(f"### {r['name']}")
            st.write(f"**Type:** {r['type']} | **Calories:** {r.get('calories','N/A')} | **Healthy:** {'✅' if r['healthy'] else '❌'}")
            st.write(f"**Ingredients:** {', '.join(r['ingredients'])}")
            with st.expander("Show Instructions"):
                st.write(r.get('instructions',''))

    # Follow-up question input
    follow_up = st.text_input("Ask a follow-up question (optional):", key="followup_input")
    if st.button("Submit Follow-up"):
        if follow_up.strip():
            st.session_state.follow_up.append(follow_up.strip())
            filters = {
                "type_filter": None,
                "healthy_only": False,
                "max_calories": None,
                "course": st.session_state.course
            }
            user_ingredients, filters = process_follow_up(follow_up, user_ingredients, filters)

            filtered_recipes = [
                r for r in recipes
                if r.get("cuisine", "").strip().lower() == sel_cuisine
            ]
            if filters["course"]:
                filtered_recipes = [
                    r for r in filtered_recipes
                    if r.get("course", "").strip().lower() == filters["course"].strip().lower()
                ]
            if filters["type_filter"]:
                filtered_recipes = [
                    r for r in filtered_recipes
                    if r.get("type", "").strip().lower() == filters["type_filter"].strip().lower()
                ]
            if filters["healthy_only"]:
                filtered_recipes = [r for r in filtered_recipes if r.get("healthy", False)]
            if filters["max_calories"]:
                filtered_recipes = [
                    r for r in filtered_recipes
                    if r.get("calories", 9999) <= filters["max_calories"]
                ]

            matched = match_recipes(user_ingredients, filtered_recipes, course=filters["course"])

            st.markdown("## 🔄 Updated Recipe Suggestions")
            if matched:
                for item in matched:
                    r = item["recipe"]
                    st.markdown(f"### {r['name']}")
                    st.write(f"**Type:** {r['type']} | **Calories:** {r.get('calories','N/A')} | **Healthy:** {'✅' if r['healthy'] else '❌'}")
                    st.write(f"**Ingredients:** {', '.join(r['ingredients'])}")
                    with st.expander("Show Instructions"):
                        st.write(r.get('instructions',''))
            else:
                st.info("No matching recipes found after your follow-up.")
