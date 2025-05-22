"""Fitness Manager agent definition."""

from google.adk.agents import LlmAgent
from google.adk.tools import google_search
from google.adk.tools.agent_tool import AgentTool

from fitness_coach.prompt import MANAGER_INSTRUCTION
from fitness_coach.tools.query_analyzer import query_analyzer
from fitness_coach.tools.response_formatter import response_formatter
from fitness_coach.tools.data_tracker import track_progress_tool, get_progress_report_tool
from fitness_coach.tools.user_profile import get_user_profile_tool, update_user_profile_tool, clear_user_profile_tool, check_missing_fields_tool
#sub_agents
from fitness_coach.sub_agents.meal_planner.agent import meal_planner
from fitness_coach.sub_agents.workout_planner.agent import workout_planner



# Configure main fitness manager to use all agents as tools but WITHOUT google_search directly
fitness_manager = LlmAgent(
    name="fitness_manager",
    model="gemini-2.0-flash",
    description="Primary agent that manages user interactions and delegates tasks to expert agents.",
    instruction=MANAGER_INSTRUCTION,
    tools=[
        query_analyzer,
        response_formatter,
        track_progress_tool,
        get_progress_report_tool,
        get_user_profile_tool,
        update_user_profile_tool,
        clear_user_profile_tool,
        check_missing_fields_tool
    ],
    sub_agents=[meal_planner, workout_planner]
)

# Define root_agent for ADK framework discovery 
root_agent = fitness_manager 