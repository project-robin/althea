"""Tool for analyzing user queries and providing appropriate agent routing."""

from typing import Dict, Any, Optional, List
from google.adk.tools import FunctionTool
from google.adk.tools.tool_context import ToolContext
import logging

logger = logging.getLogger(__name__)

def analyze_query(
    query: str,
    user_id: str,
    tool_context: ToolContext
) -> Dict[str, Any]:
    """
    Analyzes the user query and determines which expert agent(s) should handle it.
    Also includes any relevant user profile data.
    
    Args:
        query: The user's query or request
        user_id: Unique identifier for the user
        tool_context: The tool context containing any necessary information
        
    Returns:
        Dictionary with routing information and user profile data, or an error status.
    """
    try:
        # Retrieve user_profile from tool_context.state
        user_profile = tool_context.state.get("user:profile", {})
        
        # Placeholder logic - in a real implementation, this would be more sophisticated
        # and might use NLP or other techniques to better categorize the query
        query_lower = query.lower()
        
        detected_tasks: List[str] = []

        meal_keywords = [
            "meal", "diet", "nutrition", "food", "eat", "eating", "recipe", "calories", "macros",
            "breakfast", "lunch", "dinner", "snack", "meal plan", "vegetarian", "vegan", "protein",
            "carbs", "fat", "macronutrient", "indian", "mediterranean", "keto", "carbohydrate"
        ]
        workout_keywords = ["workout", "exercise", "training", "routine", "fitness", "gym", "strength", "cardio"]
        progress_keywords = ["progress", "track", "tracking", "improvement", "measurements", "weight", "record"]
        
        # Check for meal-related keywords
        if "meal plan" in query_lower or "food plan" in query_lower or "diet plan" in query_lower or \
           any(keyword in query_lower for keyword in meal_keywords):
            if "meal_plan" not in detected_tasks:
                detected_tasks.append("meal_plan")
            print(f"Query analyzer: Detected meal plan request")

        # Check for workout-related keywords
        if any(keyword in query_lower for keyword in workout_keywords):
            if "workout_plan" not in detected_tasks:
                detected_tasks.append("workout_plan")
            print(f"Query analyzer: Detected workout plan request")

        # Check for progress tracking keywords
        if any(keyword in query_lower for keyword in progress_keywords):
            if "progress_tracking" not in detected_tasks:
                detected_tasks.append("progress_tracking")
            print(f"Query analyzer: Detected progress tracking request")
            
        # If no specific tasks are detected, consider it a general query
        if not detected_tasks:
            detected_tasks.append("general")
            
        # Extract potential profile data from the query (simplified example)
        # In a real implementation, this would be more sophisticated and use NLP
        profile_data = {}
        
        # Log the detected tasks for debugging
        print(f"Query analyzer result: {detected_tasks} for query: '{query[:50]}...'")
        
        # Return routing information along with any profile data
        return {
            "detected_tasks": detected_tasks,
            "user_id": user_id,
            "profile_data": profile_data,
            "user_profile": user_profile
        }
    except Exception as e:
        logger.error(f"Error in query_analyzer tool for query '{query}': {e}")
        return {"status": "error", "message": "An error occurred while analyzing your query."}

# Define the tool that will be imported by the agent
query_analyzer = FunctionTool(
    func=analyze_query,
) 