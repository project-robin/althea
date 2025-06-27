""""Fitness Manager agent definition."""
import asyncio
import os
from google.adk.agents import LlmAgent, ParallelAgent, SequentialAgent
from google.adk.tools import google_search
from google.adk.tools.agent_tool import AgentTool
from google.adk.tools import FunctionTool
import uuid # Import the uuid library
from google.genai import types
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from dotenv import load_dotenv # Import load_dotenv
from fitness_coach.prompt import MANAGER_INSTRUCTION
from fitness_coach.tools.query_analyzer import query_analyzer
from fitness_coach.tools.data_tracker import track_progress_tool, get_progress_report_tool, save_meal_plan_tool
from fitness_coach.tools.user_profile import get_user_profile_tool, update_user_profile_tool, clear_user_profile_tool, check_missing_fields_tool
#sub_agents
from fitness_coach.sub_agents.meal_planner.agent import meal_planner
from fitness_coach.sub_agents.workout_planner.agent import workout_planner
from fitness_coach.tools.long_term_memory_tools import search_long_term_memory_tool
from fitness_coach.tools.report_synthesizer import report_synthesizer_tool
from fitness_coach.callbacks import (
    on_before_tool_use,
    on_after_tool_use,
    on_before_agent_run,
    on_after_agent_run,
    on_before_model_sending,
    on_after_model_sending,
)

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '..', '.env'))

parallel_planners = ParallelAgent(
    name="parallel_planners",
    sub_agents=[meal_planner, workout_planner]
)

def ensure_user_id(session_state):
    """Ensures a user ID exists in the session state or creates a new one."""
    import uuid
    user_id = session_state.get('user_id')
    if not user_id:
        user_id = f"user_{uuid.uuid4().hex[:8]}"
        session_state['user_id'] = user_id
        print(f"Created new user_id: {user_id}")
    return user_id


def create_root_agent():
    """Creates the root agent instance, fetching tools from the MCP server."""
    # Temporarily remove Supabase tool fetching until MCP is integrated or an alternative is chosen
    # supabase_tools, supabase_exit_stack = get_supabase_tools_async()
    # if not supabase_tools:
    #     print("--- WARNING: No Supabase tools discovered. Agent will lack Supabase functionality. ---")
    # The supabase_exit_stack should be handled by the Runner or the main application entry point
    # to ensure proper cleanup, e.g., using async with supabase_exit_stack:

    return LlmAgent(
        name="fitness_manager",
        model="gemini-2.5-flash-preview-05-20",
        description="Primary agent that manages user interactions and delegates tasks to expert agents.",
        instruction=MANAGER_INSTRUCTION,
        tools=[
            query_analyzer,
            track_progress_tool,
            get_progress_report_tool,
            get_user_profile_tool,
            update_user_profile_tool,
            clear_user_profile_tool,
            check_missing_fields_tool,
            AgentTool(meal_planner),
            AgentTool(workout_planner),
            AgentTool(parallel_planners),
            search_long_term_memory_tool,
            report_synthesizer_tool,
            save_meal_plan_tool,
        ],  # Removed supabase_tools
        before_tool_callback=on_before_tool_use,
        after_tool_callback=on_after_tool_use,
        before_agent_callback=on_before_agent_run,
        after_agent_callback=on_after_agent_run,
        before_model_callback=on_before_model_sending,
        after_model_callback=on_after_model_sending
    ), None # Changed to return None for exit_stack since supabase_exit_stack is removed


# Create the root agent factory function to be called synchronously
root_agent, _ = create_root_agent()

# Also create a reference with the expected name for backward compatibility
fitness_manager = root_agent