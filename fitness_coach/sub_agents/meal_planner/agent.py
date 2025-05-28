"""Meal Planner agent definition."""

from google.adk.agents import LlmAgent
from google.adk.tools import google_search

from fitness_coach.sub_agents.meal_planner.prompt import MEAL_PLANNER_INSTRUCTION
from fitness_coach.sub_agents.meal_planner.tools.calorie_calculator import calorie_calculator
from fitness_coach.tools.user_profile import check_missing_fields_tool

# Import other meal planner tools as they're developed
# from fitness_coach.sub_agents.meal_planner.tools.recipe_suggester import recipe_suggester
# from fitness_coach.sub_agents.meal_planner.tools.nutrition_analyzer import nutrition_analyzer

meal_planner = LlmAgent(
    name="meal_planner",
    model="gemini-2.0-flash",
    description="Expert agent specializing in creating personalized meal plans based on user goals and preferences.",
    instruction=MEAL_PLANNER_INSTRUCTION,
    tools=[
        calorie_calculator,
#        check_missing_fields_tool, # Removed as validation is handled by the manager agent
    ],
    output_key="meal_plan_result"
) 
