"""Tool for formatting responses and updating user profiles."""

import re
from typing import Dict, Any, Optional, List
from google.adk.tools import FunctionTool

def extract_workout_sections(text: str) -> Dict[str, Any]:
    """
    Extract structured sections from a workout plan text.
    """
    sections = {}
    current_section = None
    current_content = []
    
    # Common section patterns in workout plans
    section_patterns = {
        "overall_structure": r"Overall\s+Program\s+Structure:",
        "workout_breakdown": r"Workout-by-Workout\s+Breakdown:",
        "warmup": r"Warm-up\s+\(.*?\):",
        "workoutA": r"Workout\s+A\s+\(.*?\):",
        "workoutB": r"Workout\s+B\s+\(.*?\):",
        "workoutC": r"Workout\s+C\s+\(.*?\):",
        "cooldown": r"Cool-down\s+\(.*?\):",
        "guidance": r"General\s+Guidance:",
        "progression": r"Progression:",
        "tracking": r"Tracking\s+Progress:",
        "body": r"Listen\s+to\s+Your\s+Body:"
    }
    
    lines = text.split('\n')
    current_section = "intro"
    sections[current_section] = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        matched = False
        for section_key, pattern in section_patterns.items():
            if re.search(pattern, line, re.IGNORECASE):
                # Save previous section content
                if current_section:
                    sections[current_section] = current_content
                
                # Start new section
                current_section = section_key
                current_content = [line]
                matched = True
                break
                
        if not matched:
            current_content.append(line)
    
    # Save final section
    if current_section:
        sections[current_section] = current_content
        
    # Format the workout data more specifically
    structured_data = {
        "type": "workout_plan",
        "intro": "\n".join(sections.get("intro", [])),
        "structure": parse_program_structure("\n".join(sections.get("overall_structure", []))),
        "workouts": []
    }
    
    # Parse individual workouts
    for key in ["workoutA", "workoutB", "workoutC"]:
        if key in sections:
            workout_text = "\n".join(sections[key])
            workout_data = parse_workout(workout_text)
            structured_data["workouts"].append(workout_data)
            
    # Add guidance sections
    guidance_sections = ["guidance", "progression", "tracking", "body"]
    structured_data["guidance"] = {}
    for section in guidance_sections:
        if section in sections:
            title = " ".join([word.capitalize() for word in section.split("_")])
            structured_data["guidance"][section] = "\n".join(sections[section])
            
    return structured_data

def parse_program_structure(text: str) -> Dict[str, str]:
    """Parse the program structure section into key components."""
    structure = {}
    
    # Extract common program structure elements
    patterns = {
        "training_frequency": r"Training\s+Frequency:\s*(.*?)(?:\.|$|\n)",
        "workout_split": r"Workout\s+Split:\s*(.*?)(?:\.|$|\n)",
        "progression": r"Progression:\s*(.*?)(?:\.|$|\n)",
        "intensity": r"Intensity:\s*(.*?)(?:\.|$|\n)"
    }
    
    for key, pattern in patterns.items():
        match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
        if match:
            structure[key] = match.group(1).strip()
            
    return structure

def parse_workout(workout_text: str) -> Dict[str, Any]:
    """Parse an individual workout into structured data."""
    workout = {
        "name": "",
        "day": "",
        "exercises": []
    }
    
    # Extract workout name and day
    name_match = re.search(r"(Workout\s+[A-C])\s+(?:\(([^)]+)\))?", workout_text)
    if name_match:
        workout["name"] = name_match.group(1).strip()
        if name_match.group(2):
            workout["day"] = name_match.group(2).strip()
    
    # Extract exercises
    exercise_pattern = r"([^:]+):\s*(\d+\s+sets\s+of\s+\d+-\d+\s+reps)[^\.]*\.\s+Form\s+Cue:\s*([^\n]+)"
    exercises = re.findall(exercise_pattern, workout_text, re.MULTILINE)
    
    for exercise in exercises:
        workout["exercises"].append({
            "name": exercise[0].strip(),
            "sets_reps": exercise[1].strip(),
            "form_cue": exercise[2].strip()
        })
        
    return workout

def extract_meal_plan_sections(text: str) -> Dict[str, Any]:
    """
    Extract structured sections from a meal plan text.
    """
    print("Starting meal plan extraction...")
    sections = {}
    current_section = None
    current_content = []
    
    # Common section patterns in meal plans
    section_patterns = {
        "plan_summary": r"Overall\s+Plan\s+Summary:",
        "meal_breakdown": r"Meal-by-Meal\s+Breakdown:",
        "breakfast": r"Breakfast\s*\([^)]*\):",
        "mid_morning_snack": r"Mid-Morning\s+Snack\s*\([^)]*\):",
        "lunch": r"Lunch\s*\([^)]*\):",
        "evening_snack": r"Evening\s+Snack\s*\([^)]*\):",
        "dinner": r"Dinner\s*\([^)]*\):",
        "post_dinner": r"Post-Dinner\s*\([^)]*\):",
        "guidance": r"General\s+Guidance:"
    }
    
    lines = text.split('\n')
    current_section = "intro"
    sections[current_section] = []
    
    print(f"Total lines to process: {len(lines)}")
    for line_num, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
            
        matched = False
        for section_key, pattern in section_patterns.items():
            if re.search(pattern, line, re.IGNORECASE):
                print(f"Found section at line {line_num+1}: {section_key} - {line}")
                # Save previous section content
                if current_section:
                    sections[current_section] = current_content
                
                # Start new section
                current_section = section_key
                current_content = [line]
                matched = True
                break
        
        # Special handling for meal times with parentheses
        if not matched:
            meal_time_match = re.search(r"([^:]+)\s*\(([^)]+)\):", line)
            if meal_time_match and (("meal" in current_section) or current_section == "meal_breakdown"):
                meal_name = meal_time_match.group(1).strip().lower().replace(" ", "_")
                print(f"Found meal at line {line_num+1}: {meal_name} - {line}")
                # Save previous section content
                if current_section:
                    sections[current_section] = current_content
                
                # Start new section for this meal
                current_section = meal_name
                current_content = [line]
                matched = True
                
        if not matched:
            current_content.append(line)
    
    # Save final section
    if current_section:
        sections[current_section] = current_content
        
    # Format the meal plan data more specifically
    structured_data = {
        "type": "meal_plan",
        "intro": "\n".join(sections.get("intro", [])),
        "summary": parse_meal_summary("\n".join(sections.get("plan_summary", []))),
        "meals": []
    }
    
    # Parse individual meals - ensure names match the section patterns
    meal_sections = ["breakfast", "mid_morning_snack", "lunch", "evening_snack", "dinner", "post_dinner"]
    for key in meal_sections:
        if key in sections:
            meal_text = "\n".join(sections[key])
            print(f"Processing {key} section with {len(meal_text)} characters")
            meal_data = parse_meal(meal_text)
            structured_data["meals"].append(meal_data)
        else:
            # Also try alternative keys (with spaces instead of underscores)
            alt_key = key.replace("_", " ")
            if alt_key in sections:
                meal_text = "\n".join(sections[alt_key])
                print(f"Processing {alt_key} section with {len(meal_text)} characters")
                meal_data = parse_meal(meal_text)
                structured_data["meals"].append(meal_data)
            
    # Add guidance sections
    if "guidance" in sections:
        structured_data["guidance"] = "\n".join(sections["guidance"])
    
    print(f"Extracted {len(structured_data['meals'])} meals")
    # Debug: print meal names to verify extraction
    for i, meal in enumerate(structured_data['meals']):
        print(f"Meal {i+1}: {meal['name']} with dish: {meal['dish']}")
            
    return structured_data

def parse_meal_summary(text: str) -> Dict[str, Any]:
    """Parse the meal plan summary into key components."""
    summary = {}
    
    # Extract calorie information
    calories_match = re.search(r"Total\s+Daily\s+Calories:\s*(\d+)", text, re.IGNORECASE)
    if calories_match:
        summary["calories"] = int(calories_match.group(1))
    
    # Extract macronutrient breakdown
    macro_pattern = r"([^:]+):\s*(\d+)g\s*\((\d+)%\)"
    macros = re.findall(macro_pattern, text, re.MULTILINE)
    
    summary["macros"] = {}
    for macro in macros:
        name = macro[0].strip().lower()
        summary["macros"][name] = {
            "grams": int(macro[1]),
            "percentage": int(macro[2])
        }
            
    return summary

def parse_meal(meal_text: str) -> Dict[str, Any]:
    """Parse an individual meal into structured data."""
    meal = {
        "name": "",
        "time": "",
        "dish": "",
        "calories": "",
        "macros": {},
        "preparation": "",
        "substitution": ""
    }
    
    print(f"Parsing meal text: {meal_text[:100]}...")
    
    # Extract meal name and time
    name_time_match = re.search(r"([^(]+)\s*\(([^)]+)\)", meal_text)
    if name_time_match:
        meal["name"] = name_time_match.group(1).strip()
        meal["time"] = name_time_match.group(2).strip()
        print(f"Extracted meal name: {meal['name']}, time: {meal['time']}")
    else:
        # Fallback: Try to extract name from the first line
        first_line = meal_text.split('\n')[0] if '\n' in meal_text else meal_text
        if ':' in first_line:
            meal_name = first_line.split(':')[0].strip()
            meal["name"] = meal_name
            print(f"Fallback meal name extraction: {meal['name']}")
    
    # Extract dish information with multiple fallback methods
    dish_extracted = False
    
    # Method 1: Look for explicit "Dish:" label
    dish_match = re.search(r"Dish:\s*([^\n]+)", meal_text)
    if dish_match:
        meal["dish"] = dish_match.group(1).strip()
        dish_extracted = True
        print(f"Extracted dish (method 1): {meal['dish']}")
    
    # Method 2: Look for the first line after the header that's not a known label
    if not dish_extracted:
        lines = meal_text.split('\n')
        for i, line in enumerate(lines):
            if i > 0 and line.strip() and not re.search(r"(Calories|Carbs|Protein|Fat|Preparation|Substitution):", line):
                # This might be an unlabeled dish description
                meal["dish"] = line.strip()
                dish_extracted = True
                print(f"Extracted dish (method 2): {meal['dish']}")
                break
    
    # Method 3: Look for food items mentioned in the text
    if not dish_extracted:
        food_items = re.findall(r'(\d+\s*g\s+[A-Za-z]+|\d+\s*oz\s+[A-Za-z]+|\d+\s*cups?\s+[A-Za-z]+)', meal_text)
        if food_items:
            meal["dish"] = ", ".join(food_items)
            dish_extracted = True
            print(f"Extracted dish (method 3): {meal['dish']}")
    
    # If still no dish, use a generic name based on the meal type
    if not dish_extracted or not meal["dish"]:
        if "breakfast" in meal["name"].lower():
            meal["dish"] = "Balanced breakfast meal"
        elif "lunch" in meal["name"].lower():
            meal["dish"] = "Nutritious lunch option"
        elif "dinner" in meal["name"].lower():
            meal["dish"] = "Healthy dinner plate"
        elif "snack" in meal["name"].lower():
            meal["dish"] = "Healthy snack option"
        print(f"Using generic dish name: {meal['dish']}")
        
    # Extract calorie information - look for various formats
    calories_patterns = [r"Calories:\s*~?(\d+)", r"(\d+)\s*calories", r"(\d+)\s*kcal"]
    for pattern in calories_patterns:
        calories_match = re.search(pattern, meal_text, re.IGNORECASE)
        if calories_match:
            meal["calories"] = calories_match.group(1).strip()
            print(f"Extracted calories: {meal['calories']}")
            break
    
    # Fallback calorie estimation if not found
    if not meal["calories"]:
        meal["calories"] = "300-500"  # Generic estimate
        print("Using generic calorie estimate")
        
    # Extract macronutrient information - try different formats
    macros_patterns = [
        r"Carbs:\s*(\d+)g,\s*Protein:\s*(\d+)g,\s*Fat:\s*(\d+)g", 
        r"Protein:\s*(\d+)g,\s*Carbs:\s*(\d+)g,\s*Fat:\s*(\d+)g",
        r"Carbohydrates:\s*(\d+)g,\s*Protein:\s*(\d+)g,\s*Fat:\s*(\d+)g"
    ]
    for i, pattern in enumerate(macros_patterns):
        macros_match = re.search(pattern, meal_text, re.IGNORECASE)
        if macros_match:
            if i == 0:  # Carbs, Protein, Fat
                meal["macros"] = {
                    "carbs": macros_match.group(1).strip(),
                    "protein": macros_match.group(2).strip(),
                    "fat": macros_match.group(3).strip()
                }
            elif i == 1:  # Protein, Carbs, Fat
                meal["macros"] = {
                    "protein": macros_match.group(1).strip(),
                    "carbs": macros_match.group(2).strip(),
                    "fat": macros_match.group(3).strip()
                }
            elif i == 2:  # Carbohydrates, Protein, Fat
                meal["macros"] = {
                    "carbs": macros_match.group(1).strip(),
                    "protein": macros_match.group(2).strip(),
                    "fat": macros_match.group(3).strip()
                }
            print(f"Extracted macros: {meal['macros']}")
            break
    
    # Also try individual macro extraction if the combined pattern doesn't work
    if not meal["macros"]:
        carbs_match = re.search(r"Carbs:\s*(\d+)g", meal_text, re.IGNORECASE)
        protein_match = re.search(r"Protein:\s*(\d+)g", meal_text, re.IGNORECASE) 
        fat_match = re.search(r"Fat:\s*(\d+)g", meal_text, re.IGNORECASE)
        
        if carbs_match or protein_match or fat_match:
            meal["macros"] = {}
            if carbs_match:
                meal["macros"]["carbs"] = carbs_match.group(1).strip()
            if protein_match:
                meal["macros"]["protein"] = protein_match.group(1).strip() 
            if fat_match:
                meal["macros"]["fat"] = fat_match.group(1).strip()
            print(f"Extracted individual macros: {meal['macros']}")
    
    # Fallback macro values if not found
    if not meal["macros"]:
        meal["macros"] = {
            "carbs": "30",
            "protein": "20", 
            "fat": "10"
        }
        print("Using generic macro values")
        
    # Extract preparation information
    prep_match = re.search(r"Preparation:\s*([^\n]+)", meal_text)
    if prep_match:
        meal["preparation"] = prep_match.group(1).strip()
        print(f"Extracted preparation: {meal['preparation'][:30]}...")
    else:
        # Try to find preparation-like content
        prep_lines = []
        lines = meal_text.split('\n')
        in_prep_section = False
        for line in lines:
            if "how to prepare" in line.lower() or "instructions" in line.lower():
                in_prep_section = True
                continue
            if in_prep_section and line.strip():
                prep_lines.append(line.strip())
        
        if prep_lines:
            meal["preparation"] = " ".join(prep_lines)
            print(f"Found implied preparation: {meal['preparation'][:30]}...")
        else:
            meal["preparation"] = "Combine ingredients and prepare according to your preference."
            print("Using generic preparation instructions")
        
    # Extract substitution information
    sub_match = re.search(r"Substitution:\s*([^\n]+)", meal_text)
    if sub_match:
        meal["substitution"] = sub_match.group(1).strip()
        print(f"Extracted substitution: {meal['substitution'][:30]}...")
    else:
        meal["substitution"] = "Adjust ingredients based on your dietary preferences."
        print("Using generic substitution text")
        
    return meal

def format_response(
    response: str, 
    query_type: str,
    user_id: str,
    new_profile_data: Optional[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Formats a response for the user and updates the user profile if needed.
    
    Args:
        response: The raw response from an expert agent or generated by the fitness manager
        query_type: The type of query that was handled (e.g., "meal_plan", "workout_plan")
        user_id: Unique identifier for the user
        new_profile_data: Optional new data to add to the user profile
        
    Returns:
        Dictionary with formatted response and updated profile information
    """
    # Handle the default parameter within the function
    if new_profile_data is None:
        new_profile_data = {}
        
    # Format the response based on the query type
    formatted_response = response
    structured_data = None
    
    if query_type == "meal_plan":
        # Extract structured data from the meal plan
        print("Processing meal plan response...")
        structured_data = extract_meal_plan_sections(response)
        print(f"Extracted meal plan sections: {list(structured_data.keys())}")
        if "meals" in structured_data:
            print(f"Number of meals extracted: {len(structured_data['meals'])}")
            for i, meal in enumerate(structured_data["meals"]):
                print(f"Meal {i+1}: {meal.get('name', 'Unknown')}")
    elif query_type == "workout_plan":
        # Extract structured data from the workout plan
        structured_data = extract_workout_sections(response)
    elif query_type == "progress_tracking":
        # Add progress tracking-specific formatting if needed
        pass
    
    # Return formatted response along with any profile updates
    result = {
        "formatted_response": formatted_response,
        "user_id": user_id
    }
    
    # Include the structured data if we were able to extract it
    if structured_data:
        print(f"Adding structured data of type: {structured_data.get('type', 'unknown')}")
        result["structured_data"] = structured_data
    else:
        print("No structured data was extracted from the response")
    
    # Include profile updates if provided
    if new_profile_data:
        result["profile_updates"] = new_profile_data
        
    return result

# Define the tool that will be imported by the agent
response_formatter = FunctionTool(
    func=format_response,
) 