"""Tool for analyzing user queries and providing appropriate agent routing."""

from typing import Dict, Any, Optional, List
from google.adk.tools import FunctionTool

def analyze_query(
    query: str,
    user_id: str,
    user_profile: Optional[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Analyzes the user query and determines which expert agent(s) should handle it.
    Also includes any relevant user profile data.
    
    Args:
        query: The user's query or request
        user_id: Unique identifier for the user
        user_profile: Optional user profile data if already retrieved
        
    Returns:
        Dictionary with routing information and user profile data
    """
    # Handle the default parameter within the function
    if user_profile is None:
        user_profile = {}
        
    # Placeholder logic - in a real implementation, this would be more sophisticated
    # and might use NLP or other techniques to better categorize the query
    query_lower = query.lower()
    
    meal_keywords = [
        "meal", "diet", "nutrition", "food", "eat", "eating", "recipe", "calories", "macros",
        "breakfast", "lunch", "dinner", "snack", "meal plan", "vegetarian", "vegan", "protein",
        "carbs", "fat", "macronutrient", "indian", "mediterranean", "keto", "carbohydrate"
    ]
    workout_keywords = ["workout", "exercise", "training", "routine", "fitness", "gym", "strength", "cardio"]
    progress_keywords = ["progress", "track", "tracking", "improvement", "measurements", "weight", "record"]
    
    # Determine the query type
    query_type = "general"
    
    # Check for explicit meal plan requests first
    if "meal plan" in query_lower or "food plan" in query_lower or "diet plan" in query_lower:
        query_type = "meal_plan"
        print(f"Query analyzer: Detected explicit meal plan request")
    # Then check for other meal-related keywords
    elif any(keyword in query_lower for keyword in meal_keywords):
        query_type = "meal_plan"
        print(f"Query analyzer: Detected meal plan request based on keywords")
    # Check for workout-related keywords
    elif any(keyword in query_lower for keyword in workout_keywords):
        query_type = "workout_plan"
        print(f"Query analyzer: Detected workout plan request")
    # Check for progress tracking keywords
    elif any(keyword in query_lower for keyword in progress_keywords):
        query_type = "progress_tracking"
        print(f"Query analyzer: Detected progress tracking request")
        
    # Extract potential profile data from the query (simplified example)
    # In a real implementation, this would be more sophisticated and use NLP
    profile_data = {}
    
    # Log the query type for debugging
    print(f"Query analyzer result: {query_type} for query: '{query[:50]}...'")
    
    # Return routing information along with any profile data
    return {
        "query_type": query_type,
        "user_id": user_id,
        "profile_data": profile_data,
        "user_profile": user_profile
    }

# Define the tool that will be imported by the agent
query_analyzer = FunctionTool(
    func=analyze_query,
) 