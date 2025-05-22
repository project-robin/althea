"""Workout Planner agent definition."""

from google.adk.agents import LlmAgent
from google.adk.tools import google_search

from fitness_coach.sub_agents.workout_planner.prompt import WORKOUT_PLANNER_INSTRUCTION
from fitness_coach.sub_agents.workout_planner.tools.exercise_selector import exercise_selector
from fitness_coach.tools.user_profile import check_missing_fields_tool

# Import other workout planner tools as they're developed
# from fitness_coach.sub_agents.workout_planner.tools.workout_scheduler import workout_scheduler
# from fitness_coach.sub_agents.workout_planner.tools.progress_calculator import progress_calculator

workout_planner = LlmAgent(
    name="workout_planner",
    model="gemini-2.0-flash",
    description="Expert agent specializing in creating personalized workout routines based on user goals and fitness level.",
    instruction=WORKOUT_PLANNER_INSTRUCTION,
    tools=[
        exercise_selector,
        check_missing_fields_tool,
    ],
) 