""""Fitness Manager agent definition."""
import asyncio
import os
from google.adk.agents import LlmAgent, ParallelAgent, SequentialAgent
from google.adk.tools import google_search
from google.adk.tools.agent_tool import AgentTool
from google.adk.tools import FunctionTool
import uuid # Import the uuid library
from google.genai import types
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from dotenv import load_dotenv # Import load_dotenv
from fitness_coach.prompt import MANAGER_INSTRUCTION
from fitness_coach.tools.query_analyzer import query_analyzer
from fitness_coach.tools.data_tracker import track_progress_tool, get_progress_report_tool
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


async def get_supabase_tools_async():
    """Connects to the mcp-supabase server via npx and returns the tools and exit stack."""
    print("--- Attempting to start and connect to mcp-supabase MCP server via npx ---")
    try:
        # Check if uvx is available (basic check)
        await asyncio.create_subprocess_shell('npx --version', stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        tools, exit_stack = await MCPToolset.from_server(
            connection_params=StdioServerParameters(
                command='npx',
                args=["-y",
                    "@supabase/mcp-server-supabase@latest",
                    "--access-token",
                    "sbp_a58e61321d349cfce1f7c8931929cc4d5ff2bdbc"],
            )
        )
        print(f"--- Successfully connected to mcp-supabase server. Discovered {len(tools)} tool(s). ---")
        for tool in tools:
            print(f"  - Discovered tool: {tool.name}")
        return tools, exit_stack
    except FileNotFoundError:
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print("!!! ERROR: 'npx' command not found. Please install npx: pip install npx !!!")
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        class DummyExitStack:
            async def __aenter__(self): return self
            async def __aexit__(self, *args): pass
        return [], DummyExitStack()
    except Exception as e:
        print(f"--- ERROR connecting to or starting mcp-supabase server: {e} ---")
        class DummyExitStack:
            async def __aenter__(self): return self
            async def __aexit__(self, *args): pass
        return [], DummyExitStack()


def create_root_agent_sync():
    """Creates the root agent instance synchronously with basic tools (no MCP)."""
    print("--- Creating root agent without MCP tools (synchronous initialization) ---")

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
        ],  # No MCP tools for now to avoid async issues
        before_tool_callback=on_before_tool_use,
        after_tool_callback=on_after_tool_use,
        before_agent_callback=on_before_agent_run,
        after_agent_callback=on_after_agent_run,
        before_model_callback=on_before_model_sending,
        after_model_callback=on_after_model_sending
    )


async def create_root_agent_with_mcp():
    """Creates the root agent instance after fetching tools from the MCP server."""
    supabase_tools, supabase_exit_stack = await get_supabase_tools_async()
    # Optionally, you can add a check here if supabase_tools are crucial
    if not supabase_tools:
        print("--- WARNING: No supabase tools discovered. Agent will lack supabase functionality. ---")

    # Ensure the reddit_exit_stack is properly managed.
    # In a full application, this would typically be handled by the Runner or main execution loop.
    # For this example, we'll just return it along with the agent.

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
        ] + supabase_tools,  # Add the dynamically fetched supabase tools
        before_tool_callback=on_before_tool_use,
        after_tool_callback=on_after_tool_use,
        before_agent_callback=on_before_agent_run,
        after_agent_callback=on_after_agent_run,
        before_model_callback=on_before_model_sending,
        after_model_callback=on_after_model_sending
    ), supabase_exit_stack


# Create the root agent synchronously to avoid coroutine issues
root_agent = create_root_agent_sync()

# Also create a reference with the expected name for backward compatibility
fitness_manager = root_agent

# The supabase_mcp_exit_stack should be handled by the Runner or the main application entry point
# to ensure proper cleanup, e.g., using async with supabase_mcp_exit_stack: