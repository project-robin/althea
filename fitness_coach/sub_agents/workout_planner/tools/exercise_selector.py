"""Tool for selecting appropriate exercises based on user parameters."""

from typing import Dict, List, Literal, Optional, Any
from google.adk.tools import FunctionTool

ExperienceLevelType = Literal["beginner", "intermediate", "advanced"]
WorkoutLocationType = Literal["home", "gym", "outdoors"]
MuscleGroupType = Literal["chest", "back", "arms", "shoulders", "legs", "core", "full_body", "cardio"]

def select_exercises(
    experience_level: ExperienceLevelType,
    workout_location: WorkoutLocationType,
    target_muscle_groups: List[MuscleGroupType],
    available_equipment: Optional[List[str]] = None,
    time_available_minutes: Optional[int] = None,
    exclude_exercises: Optional[List[str]] = None,
    training_goal: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Selects appropriate exercises based on user parameters.
    
    Args:
        experience_level: User's training experience level
        workout_location: Where the workout will be performed
        target_muscle_groups: List of muscle groups to target
        available_equipment: Optional list of available equipment
        time_available_minutes: Optional time available for workout in minutes
        exclude_exercises: Optional list of exercises to exclude
        training_goal: Optional specific training goal
        
    Returns:
        Dictionary with selected exercises, workout structure, and estimated duration
    """
    # Handle default values if not provided
    if time_available_minutes is None:
        time_available_minutes = 60
    if training_goal is None:
        training_goal = "general_fitness"

    # This is a placeholder - in a real implementation, this would select 
    # exercises from a database based on the provided parameters
    
    # Example response format
    return {
        "exercises": [
            {
                "name": "Push-ups",
                "sets": 3,
                "reps": "10-12",
                "rest_seconds": 60,
                "muscle_group": "chest",
            },
            {
                "name": "Bodyweight Squats",
                "sets": 3,
                "reps": "15-20",
                "rest_seconds": 60,
                "muscle_group": "legs",
            },
        ],
        "duration_minutes": time_available_minutes, # Use the potentially defaulted value
        "difficulty": experience_level,
        "equipment_needed": ["none"],
    }

exercise_selector = FunctionTool(
    func=select_exercises,
) 