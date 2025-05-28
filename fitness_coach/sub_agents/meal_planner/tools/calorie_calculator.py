"""Tool for calculating calorie and macronutrient needs."""

from typing import Dict, Literal, Optional, Any
from google.adk.tools import FunctionTool

GenderType = Literal["male", "female", "other"]
ActivityLevelType = Literal["sedentary", "light", "moderate", "active", "very_active"]
GoalType = Literal["weight_loss", "maintenance", "muscle_gain"]

def calculate_nutrition_needs(
    age: int,
    gender: GenderType,
    weight_kg: float,
    height_cm: float,
    activity_level: ActivityLevelType,
    goal: GoalType,
    weight_loss_rate: Optional[float],
    muscle_gain_rate: Optional[float],
) -> Dict[str, Any]:
    """
    Calculates daily calorie and macronutrient needs based on user attributes and goals.
    
    Args:
        age: User's age in years
        gender: User's gender for BMR calculation
        weight_kg: User's weight in kilograms
        height_cm: User's height in centimeters
        activity_level: User's general activity level
        goal: User's primary goal
        weight_loss_rate: Target kg per week to lose (for weight loss)
        muscle_gain_rate: Target kg per week to gain (for muscle gain)
        
    Returns:
        Dictionary with calculated calories and macronutrient breakdown
    """
    # Calculate BMR using Mifflin-St Jeor Equation
    if gender == "male":
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
    elif gender == "female":
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age - 161
    else:
        # For non-binary individuals, use average of male and female equations
        bmr_male = 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
        bmr_female = 10 * weight_kg + 6.25 * height_cm - 5 * age - 161
        bmr = (bmr_male + bmr_female) / 2
    
    # Apply activity multiplier to calculate TDEE
    activity_multipliers = {
        "sedentary": 1.2,       # Little or no exercise
        "light": 1.375,         # Light exercise 1-3 days/week
        "moderate": 1.55,       # Moderate exercise 3-5 days/week
        "active": 1.725,        # Heavy exercise 6-7 days/week
        "very_active": 1.9      # Very heavy exercise, physical job or twice daily training
    }
    
    tdee = bmr * activity_multipliers[activity_level]
    
    # Adjust calories based on goal
    # Default calorie adjustments
    if goal == "weight_loss":
        # Standard deficit is 500 calories, but adjust if weight_loss_rate is specified
        deficit = 500 if weight_loss_rate is None else weight_loss_rate * 1100
        # Cap deficit to ensure safe weight loss (not below 1200 for women, 1500 for men)
        min_calories = 1200 if gender == "female" else 1500
        calories = max(min_calories, tdee - deficit)
    elif goal == "maintenance":
        calories = tdee
    elif goal == "muscle_gain":
        # Standard surplus is 300 calories, but adjust if muscle_gain_rate is specified
        surplus = 300 if muscle_gain_rate is None else muscle_gain_rate * 500
        calories = tdee + surplus
    
    # Round calories to nearest 10
    calories = round(calories / 10) * 10
    
    # Calculate macronutrients
    # Protein requirements vary by goal
    if goal == "weight_loss":
        # Higher protein for weight loss to preserve muscle
        protein_pct = 35
        fat_pct = 30
        carbs_pct = 35
    elif goal == "maintenance":
        protein_pct = 30
        fat_pct = 30 
        carbs_pct = 40
    elif goal == "muscle_gain":
        # Higher protein and carbs for muscle gain
        protein_pct = 30
        fat_pct = 25
        carbs_pct = 45
    
    # Calculate grams for each macronutrient
    protein_g = round((calories * protein_pct / 100) / 4)  # 4 calories per gram of protein
    fat_g = round((calories * fat_pct / 100) / 9)         # 9 calories per gram of fat
    carbs_g = round((calories * carbs_pct / 100) / 4)     # 4 calories per gram of carbs
    
    return {
        "calories": int(calories),
        "protein_g": protein_g,
        "carbs_g": carbs_g, 
        "fat_g": fat_g,
        "protein_pct": protein_pct,
        "carbs_pct": carbs_pct,
        "fat_pct": fat_pct,
    }

calorie_calculator = FunctionTool(
    func=calculate_nutrition_needs,
)