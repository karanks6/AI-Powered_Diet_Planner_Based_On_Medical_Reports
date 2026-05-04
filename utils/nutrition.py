ACTIVITY_MULTIPLIERS = {
    "sedentary": 1.2,
    "light": 1.375,
    "moderate": 1.55,
    "active": 1.725,
    "very_active": 1.9
}

def harris_benedict_bmr(sex, weight_kg, height_cm, age):
    if sex.lower().startswith("m"):
        return 88.362 + (13.397 * weight_kg) + (4.799 * height_cm) - (5.677 * age)
    return 447.593 + (9.247 * weight_kg) + (3.098 * height_cm) - (4.330 * age)

def calculate_tdee(sex, weight_kg, height_cm, age, activity):
    bmr = harris_benedict_bmr(sex, weight_kg, height_cm, age)
    mult = ACTIVITY_MULTIPLIERS.get(activity, 1.2)
    return bmr * mult

def macro_split(calories, protein_pct=20, fat_pct=25, carb_pct=55):
    protein_g = (calories * (protein_pct/100.0)) / 4.0
    fat_g = (calories * (fat_pct/100.0)) / 9.0
    carbs_g = (calories * (carb_pct/100.0)) / 4.0
    return {"protein_g": round(protein_g,1), "fat_g": round(fat_g,1), "carbs_g": round(carbs_g,1)}

def macro_split(calories, conditions=None, activity="moderate"):
    """
    Smart macro distribution based on health conditions and activity level.
    Returns a dict with calories, protein, carbs, and fat in grams.
    """

    if conditions is None:
        conditions = {}

    # Default balanced macros (in % of total calories)
    macros = {
        "protein_pct": 25,
        "carbs_pct": 50,
        "fat_pct": 25
    }

    # Adjust macros based on conditions
    # Each condition modifies the percentages slightly
    if conditions.get("diabetes", 0) > 0.5:
        macros.update({
            "carbs_pct": 40,
            "protein_pct": 30,
            "fat_pct": 30
        })
    if conditions.get("obesity", 0) > 0.5:
        macros.update({
            "carbs_pct": 35,
            "protein_pct": 35,
            "fat_pct": 30
        })
    if conditions.get("heart_disease", 0) > 0.5 or conditions.get("hypertension", 0) > 0.5:
        macros.update({
            "carbs_pct": 50,
            "protein_pct": 25,
            "fat_pct": 25
        })
    if conditions.get("liver_disease", 0) > 0.5:
        macros.update({
            "carbs_pct": 55,
            "protein_pct": 20,
            "fat_pct": 25
        })
    if conditions.get("kidney_disease", 0) > 0.5:
        macros.update({
            "carbs_pct": 55,
            "protein_pct": 20,
            "fat_pct": 25
        })
    if conditions.get("anemia", 0) > 0.5:
        macros.update({
            "carbs_pct": 50,
            "protein_pct": 30,
            "fat_pct": 20
        })
    if conditions.get("thyroid_disorder", 0) > 0.5:
        macros.update({
            "carbs_pct": 45,
            "protein_pct": 30,
            "fat_pct": 25
        })

    # Adjust for activity level
    activity = activity.lower()
    if activity in ["active", "very_active"]:
        macros["protein_pct"] += 5
        macros["carbs_pct"] += 5
        macros["fat_pct"] -= 10
    elif activity == "sedentary":
        macros["protein_pct"] -= 5
        macros["carbs_pct"] += 5
        # keep fat same

    # Ensure total = 100%
    total_pct = macros["protein_pct"] + macros["carbs_pct"] + macros["fat_pct"]
    for k in ["protein_pct", "carbs_pct", "fat_pct"]:
        macros[k] = (macros[k] / total_pct) * 100

    # Convert to grams (assuming 4 kcal/g for protein & carbs, 9 kcal/g for fat)
    protein_g = (macros["protein_pct"] / 100) * calories / 4
    carbs_g = (macros["carbs_pct"] / 100) * calories / 4
    fat_g = (macros["fat_pct"] / 100) * calories / 9

    return {
        "protein": round(protein_g, 1),
        "carbs": round(carbs_g, 1),
        "fat": round(fat_g, 1),
        "ratios": {
            "protein_pct": round(macros["protein_pct"], 1),
            "carbs_pct": round(macros["carbs_pct"], 1),
            "fat_pct": round(macros["fat_pct"], 1)
        }
    }

