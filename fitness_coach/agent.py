"""Fitness Manager agent definition."""

from google.adk.agents import LlmAgent, ParallelAgent, SequentialAgent
from google.adk.tools import google_search
from google.adk.tools.agent_tool import AgentTool
from google.adk.tools import FunctionTool

from fitness_coach.prompt import MANAGER_INSTRUCTION
from fitness_coach.tools.query_analyzer import query_analyzer
from fitness_coach.tools.data_tracker import track_progress_tool, get_progress_report_tool
from fitness_coach.tools.user_profile import get_user_profile_tool, update_user_profile_tool, clear_user_profile_tool, check_missing_fields_tool
#sub_agents
from fitness_coach.sub_agents.meal_planner.agent import meal_planner
from fitness_coach.sub_agents.workout_planner.agent import workout_planner
# Import the new long-term memory tool
from fitness_coach.tools.long_term_memory_tools import search_long_term_memory_tool
# Import the new report synthesizer tool
from fitness_coach.tools.report_synthesizer import report_synthesizer_tool

# Define a ParallelAgent to run meal_planner and workout_planner concurrently
parallel_planners = ParallelAgent(
    name="parallel_planners",
    sub_agents=[meal_planner, workout_planner]
)

# Remove the SequentialAgent definition
# Define the SequentialAgent that orchestrates planning and synthesis
# system_monitor_agent = SequentialAgent(
#     name="system_monitor_agent",
#     sub_agents=[
#         parallel_planners,
#         # Remove result_formatter_agent from sub_agents
#         # result_formatter_agent # Use the new formatting agent here
#     ],
# )

# The fitness_manager agent is the root agent and calls system_monitor_agent as a tool.
fitness_manager = LlmAgent(
    name="fitness_manager",
    model="gemini-2.5-flash-preview-05-20",
    description="Primary agent that manages user interactions and delegates tasks to expert agents. Can access long-term user history.",
    instruction=MANAGER_INSTRUCTION,
    
    tools=[
        query_analyzer,
        # Remove response_formatter from fitness_manager tools, it's called internally now
        track_progress_tool,
        get_progress_report_tool,
        get_user_profile_tool,
        update_user_profile_tool,
        clear_user_profile_tool,
        check_missing_fields_tool,
       ## response_formatter_tool,    
       # Remove the AgentTool for system_monitor_agent
       # AgentTool(system_monitor_agent), # Call the orchestrator as a tool
       AgentTool(meal_planner), # Add meal_planner as a tool
       AgentTool(workout_planner), # Add workout_planner as a tool
       AgentTool(parallel_planners), # Keep parallel_planners as a tool
       search_long_term_memory_tool, # Add the new long-term memory search tool
       report_synthesizer_tool, # Add the report synthesizer tool
    ]
    # sub_agents are now called as tools by the fitness_manager
   # sub_agents=[system_monitor_agent],
)

# The root_agent for ADK framework discovery is the fitness_manager
root_agent = fitness_manager 