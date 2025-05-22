"""Tool for managing user profile data and sharing between agents."""

from typing import Dict, Any, Optional, List, Set
from google.adk.tools import FunctionTool

# User profile dictionary to store user data
# This will be in memory but could be extended to use persistent storage
user_profiles = {}

# Define required profile fields for different contexts
REQUIRED_FIELDS = {
    "basic": {
        "age", "gender", "height_cm", "weight_kg"
    },
    "meal_planning": {
        "age", "gender", "height_cm", "weight_kg", "activity_level", 
        "goal", "dietary_restrictions", "food_preferences"
    },
    "workout_planning": {
        "age", "gender", "height_cm", "weight_kg", "activity_level", 
        "goal", "fitness_level", "available_equipment", "exercise_preferences"
    }
}

def get_user_profile(
    user_id: str,
) -> Dict[str, Any]:
    """
    Retrieves a user's profile data.
    
    Args:
        user_id: Identifier for the user
        
    Returns:
        Dictionary with the user's profile data or empty dict if not found
    """
    if user_id not in user_profiles:
        user_profiles[user_id] = {}
        
    return user_profiles[user_id]

def update_user_profile(
    user_id: str,
    data: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Updates a user's profile with new data.
    
    Args:
        user_id: Identifier for the user
        data: The data to add/update in the profile
        
    Returns:
        Dictionary with the updated user profile
    """
    if user_id not in user_profiles:
        user_profiles[user_id] = {}
        
    # Update the profile with new data
    user_profiles[user_id].update(data)
    
    return user_profiles[user_id]

def clear_user_profile(
    user_id: str,
) -> Dict[str, Any]:
    """
    Clears a user's profile data.
    
    Args:
        user_id: Identifier for the user
        
    Returns:
        Empty dictionary
    """
    user_profiles[user_id] = {}
    
    return user_profiles[user_id]

def check_missing_fields(
    user_id: str,
    context: str
) -> List[str]:
    """
    Checks which required fields are missing from a user's profile for a specific context.
    
    Args:
        user_id: Identifier for the user
        context: The context to check required fields for ('basic', 'meal_planning', or 'workout_planning')
        
    Returns:
        List of missing field names
    """
    if user_id not in user_profiles:
        user_profiles[user_id] = {}
    
    # Handle default value inside the function instead of in the parameter
    if context is None:
        context = "basic"
        
    if context not in REQUIRED_FIELDS:
        return []
    
    required = REQUIRED_FIELDS[context]
    existing = set(user_profiles[user_id].keys())
    
    return list(required - existing)

# Define the individual tools that will be imported by the agent
get_user_profile_tool = FunctionTool(
    func=get_user_profile,
)

update_user_profile_tool = FunctionTool(
    func=update_user_profile,
)

clear_user_profile_tool = FunctionTool(
    func=clear_user_profile,
)

check_missing_fields_tool = FunctionTool(
    func=check_missing_fields,
) 