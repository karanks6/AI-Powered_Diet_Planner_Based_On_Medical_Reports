import json
import random
import os

def load_food_database():
    """Safely load the Indian food dataset."""
    db_path = os.path.join("data", "indian_food_db.json")
    if not os.path.exists(db_path):
        print(f"[ERROR] Food database not found at {db_path}")
        return []
    with open(db_path, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError as e:
            print(f"[ERROR] JSON decode error in food database: {e}")
            return []


def filter_meals(food_db, diet_type, region, detected_conditions):
    """
    Filters meals based on diet type, region, and therapeutic needs.
    Ensures medical compatibility and user preference relevance.
    """
    # ✅ Safe hierarchy for allowed diets
    diet_hierarchy = {
        "jain": ["jain"],
        "vegan": ["vegan", "vegetarian"],
        "vegetarian": ["vegetarian", "jain"],
        "eggetarian": ["eggetarian", "vegetarian"],
        "non_vegetarian": ["non_vegetarian", "eggetarian", "vegetarian"],
    }

    allowed_diets = diet_hierarchy.get(diet_type.lower(), ["vegetarian"])
    meals = []


    # 🧩 Filter by diet, region, and therapeutic tags
    for meal in food_db:
        meal_diet = meal.get("diet_type", "").lower()
        meal_region = meal.get("region", "mixed").lower()

        if meal_diet not in allowed_diets:
            continue
        if region != "mixed" and meal_region != region:
            continue

        # 💊 Medical relevance
        condition_tags = []
        for condition, present in detected_conditions.items():
            if present >= 1.0:
                if condition == "diabetes":
                    condition_tags += ["low_gi", "high_fiber"]
                elif condition == "hypertension":
                    condition_tags += ["low_sodium", "high_potassium"]
                elif condition == "heart_disease":
                    condition_tags += ["omega3", "low_fat"]
                elif condition == "obesity":
                    condition_tags += ["low_calorie", "high_protein"]
                elif condition == "anemia":
                    condition_tags += ["iron_rich"]
                elif condition == "thyroid_disorder":
                    condition_tags += ["iodine_rich"]
                elif condition == "liver_disease":
                    condition_tags += ["antioxidant_rich", "low_fat"]
                elif condition == "kidney_disease":
                    condition_tags += ["low_protein", "low_sodium"]

        tag_match_score = len(set(meal.get("tags", [])) & set(condition_tags))
        if tag_match_score >= 1 or not condition_tags:
            meals.append(meal)

    # 🩹 Fallback if few meals found
    if len(meals) < 10:
        print("[WARN] Few therapeutic matches found. Expanding selection.")
        meals = [m for m in food_db if m.get("diet_type", "").lower() in allowed_diets]

    random.shuffle(meals)
    return meals


def ensure_preference_meal(day_meals, food_db, user_pref):
    """
    Ensures at least one meal per day matches the user's main diet type.
    If none exist, replaces a random meal with one that matches the preference.
    """
    primary_type = user_pref.lower()

    # ✅ If already contains a meal of user preference, return as-is
    if any(meal.get("diet_type", "").lower() == primary_type for meal in day_meals):
        return day_meals

    # ✅ Filter preferred meals
    preferred_meals = [
        m for m in food_db
        if m.get("diet_type", "").lower() == primary_type
    ]

    if not preferred_meals:
        print(f"[INFO] No exact match for {primary_type}, keeping meals as-is.")
        return day_meals

    # ✅ Replace a random meal with a preferred meal
    replacement = random.choice(preferred_meals)
    replace_index = random.randrange(len(day_meals))
    replaced = day_meals[replace_index]
    day_meals[replace_index] = replacement

    print(f"[INFO] Replaced '{replaced.get('dish', '')}' with '{replacement.get('dish', '')}' "
          f"to include {primary_type} preference.")
    return day_meals

def generate_plan(profile, detected_conditions, nutrition_targets):
    """
    Generates a personalized daily or weekly diet plan.
    Each day includes at least one meal of the user's selected diet preference.
    """
    food_db = load_food_database()
    if not food_db:
        print("[ERROR] Empty food database. Cannot generate plan.")
        return {}

    diet_type = profile.get("dietary_pref", "vegetarian").lower()
    region = profile.get("regional_pref", "mixed").lower()
    plan_type = profile.get("plan_type", "daily").lower()

    filtered_meals = filter_meals(food_db, diet_type, region, detected_conditions)
    plan = {}
    meal_times = ["breakfast", "lunch", "dinner"]

    if plan_type == "daily":
        day_meals = []
        for time in meal_times:
            candidates = [
                m for m in filtered_meals
                if m.get("meal_time", "").lower() == time
            ]
            if candidates:
                meal = random.choice(candidates)
                day_meals.append(meal)
        # ✅ Enforce preference inclusion
        day_meals = ensure_preference_meal(day_meals, food_db, diet_type)
        plan["Day 1"] = day_meals

    elif plan_type == "weekly":
        for day in range(1, 8):
            day_meals = []
            for time in meal_times:
                candidates = [
                    m for m in filtered_meals
                    if m.get("meal_time", "").lower() == time
                ]
                if candidates:
                    meal = random.choice(candidates)
                    day_meals.append(meal)
                    filtered_meals.remove(meal)
            # ✅ Guarantee user preference meal each day
            day_meals = ensure_preference_meal(day_meals, food_db, diet_type)
            plan[f"Day {day}"] = day_meals

    return plan

