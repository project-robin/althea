"""Tool for managing user profile data and sharing between agents."""

from typing import Dict, Any, Optional, List, Set
from google.adk.tools import FunctionTool, ToolContext
import logging

logger = logging.getLogger(__name__)

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
    tool_context: ToolContext
) -> Dict[str, Any]:
    """
    Retrieves a user's profile data from session state.
    
    Args:
        user_id: Identifier for the user
        tool_context: The context object providing access to session state.
        
    Returns:
        Dictionary with the user's profile data or empty dict if not found, or an error status.
    """
    try:
        return tool_context.state.get(f"user_profile_{user_id}", {})
    except Exception as e:
        logger.error(f"Error retrieving profile for user {user_id}: {e}")
        return {"status": "error", "message": "An error occurred while retrieving your profile."}

def update_user_profile(
    user_id: str,
    data: Dict[str, Any],
    tool_context: ToolContext
) -> Dict[str, Any]:
    """
    Updates a user's profile data in session state.

    Args:
        user_id: Identifier for the user
        data: Dictionary containing profile data to update (e.g., {"age": 30, "weight_kg": 80})
        tool_context: The context object providing access to session state.

    Returns:
        Dictionary with the updated user's profile data, or an error status.
    """
    try:
        current_profile = tool_context.state.get(f"user_profile_{user_id}", {})

        standardized_data = {}
        for key, value in data.items():
            if key == "height":
                standardized_data["height_cm"] = value
            elif key == "weight":
                standardized_data["weight_kg"] = value
            elif key == "weight_loss_goal":
                standardized_data["goal"] = value
            else:
                standardized_data[key] = value

        current_profile.update(standardized_data)
        tool_context.state[f"user_profile_{user_id}"] = current_profile

        return current_profile
    except Exception as e:
        logger.error(f"Error updating profile for user {user_id} with data {data}: {e}")
        return {"status": "error", "message": "An error occurred while updating your profile."}

def clear_user_profile(
    user_id: str,
    tool_context: ToolContext
) -> Dict[str, Any]:
    """
    Clears a user's profile data from session state.
    
    Args:
        user_id: Identifier for the user
        tool_context: The context object providing access to session state.
        
    Returns:
        Empty dictionary on success, or an error status.
    """
    try:
        if f"user_profile_{user_id}" in tool_context.state:
            del tool_context.state[f"user_profile_{user_id}"]

        return {}
    except Exception as e:
        logger.error(f"Error clearing profile for user {user_id}: {e}")
        return {"status": "error", "message": "An error occurred while clearing your profile."}

def check_missing_fields(
    user_id: str,
    context: str,
    tool_context: ToolContext
) -> Dict[str, Any] | List[str]:
    """
    Checks which required fields are missing from a user's profile in session state for a specific context.
    
    Args:
        user_id: Identifier for the user
        context: The context to check required fields for ('basic', 'meal_planning', or 'workout_planning')
        tool_context: The context object providing access to session state.

    Returns:
        List of missing field names on success, or an error status.
    """
    try:
        current_profile = tool_context.state.get(f"user_profile_{user_id}", {})

        if context is None:
            context = "basic"
            
        if context not in REQUIRED_FIELDS:
            # Log a warning if an unexpected context is provided but return an empty list
            logger.warning(f"Unknown context '{context}' provided to check_missing_fields for user {user_id}.")
            return []

        required = REQUIRED_FIELDS[context]
        existing = set(current_profile.keys())

        return list(required - existing)
    except Exception as e:
        logger.error(f"Error checking missing fields for user {user_id} with context '{context}': {e}")
        return {"status": "error", "message": "An error occurred while checking for missing profile fields."}

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