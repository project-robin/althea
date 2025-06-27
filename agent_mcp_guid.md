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
        # Check if npx is available
        proc = await asyncio.create_subprocess_shell(
            'npx --version', 
            stdout=asyncio.subprocess.PIPE, 
            stderr=asyncio.subprocess.PIPE
        )
        await proc.communicate()
        
        if proc.returncode != 0:
            raise FileNotFoundError("npx command failed")
            
        # Create the MCP toolset with proper connection parameters
        toolset_and_exit = await MCPToolset.from_server(
            connection_params=StdioServerParameters(
                command='npx',
                args=[
                    "-y",
                    "@supabase/mcp-server-supabase@latest",
                    "--access-token",
                    "sbp_a58e61321d349cfce1f7c8931929cc4d5ff2bdbc"
                ],
                # Add environment variables if needed
                env=dict(os.environ)
            )
        )
        
        tools, exit_stack = toolset_and_exit
        print(f"--- Successfully connected to mcp-supabase server. Discovered {len(tools)} tool(s). ---")
        for tool in tools:
            print(f"  - Discovered tool: {tool.name}")
        return tools, exit_stack
        
    except FileNotFoundError:
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print("!!! ERROR: 'npx' command not found. Please install Node.js and npm first !!!")
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        return [], None
    except Exception as e:
        print(f"--- ERROR connecting to or starting mcp-supabase server: {e} ---")
        return [], None


def get_base_tools():
    """Get the base tools that don't require MCP."""
    return [
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
    ]


def create_root_agent_sync():
    """Creates the root agent instance synchronously with basic tools (no MCP)."""
    print("--- Creating root agent without MCP tools (synchronous initialization) ---")

    return LlmAgent(
        name="fitness_manager",
        model="gemini-2.5-flash-preview-05-20",
        description="Primary agent that manages user interactions and delegates tasks to expert agents.",
        instruction=MANAGER_INSTRUCTION,
        tools=get_base_tools(),
        before_tool_callback=on_before_tool_use,
        after_tool_callback=on_after_tool_use,
        before_agent_callback=on_before_agent_run,
        after_agent_callback=on_after_agent_run,
        before_model_callback=on_before_model_sending,
        after_model_callback=on_after_model_sending
    )


async def create_root_agent_with_mcp():
    """Creates the root agent instance after fetching tools from the MCP server."""
    print("--- Creating root agent with MCP tools (asynchronous initialization) ---")
    
    # Get base tools
    base_tools = get_base_tools()
    
    # Try to get MCP tools
    supabase_tools, supabase_exit_stack = await get_supabase_tools_async()
    
    # Combine tools
    all_tools = base_tools
    if supabase_tools:
        all_tools.extend(supabase_tools)
        print(f"--- Added {len(supabase_tools)} MCP tools to agent ---")
    else:
        print("--- WARNING: No supabase tools discovered. Agent will lack supabase functionality. ---")

    agent = LlmAgent(
        name="fitness_manager",
        model="gemini-2.5-flash-preview-05-20",
        description="Primary agent that manages user interactions and delegates tasks to expert agents.",
        instruction=MANAGER_INSTRUCTION,
        tools=all_tools,
        before_tool_callback=on_before_tool_use,
        after_tool_callback=on_after_tool_use,
        before_agent_callback=on_before_agent_run,
        after_agent_callback=on_after_agent_run,
        before_model_callback=on_before_model_sending,
        after_model_callback=on_after_model_sending
    )
    
    return agent, supabase_exit_stack


# Create the root agent synchronously for backward compatibility
root_agent = create_root_agent_sync()
fitness_manager = root_agent


# Async entry point for running with MCP
async def create_fitness_manager_with_mcp():
    """
    Async factory function to create fitness manager agent with MCP tools.
    Use this in your main application when you want MCP functionality.
    
    Example usage:
    ```python
    async def main():
        agent, exit_stack = await create_fitness_manager_with_mcp()
        async with exit_stack:
            # Use the agent here
            runner = Runner(agent)
            await runner.run("Create a workout plan")
    ```
    """
    return await create_root_agent_with_mcp()


# Alternative pattern for async initialization
class FitnessManagerFactory:
    """Factory class for creating fitness manager agents with optional MCP support."""
    
    @staticmethod
    def create_sync():
        """Create agent without MCP tools (synchronous)."""
        return create_root_agent_sync()
    
    @staticmethod
    async def create_with_mcp():
        """Create agent with MCP tools (asynchronous)."""
        return await create_root_agent_with_mcp()


# Example usage in your main application:
"""
# For synchronous usage (no MCP):
agent = FitnessManagerFactory.create_sync()

# For asynchronous usage (with MCP):
async def main():
    agent, exit_stack = await FitnessManagerFactory.create_with_mcp()
    async with exit_stack:
        # Your application logic here
        runner = Runner(agent)
        result = await runner.run("Hello")
        print(result)

if __name__ == "__main__":
    asyncio.run(main())
"""
Now, let me also create a proper main entry point file that shows how to run the agent with MCP:
"""
Main entry point for running the Fitness Manager agent with MCP support.
"""
import asyncio
import sys
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from fitness_coach.agent import create_fitness_manager_with_mcp, FitnessManagerFactory


async def run_with_mcp():
    """Run the fitness manager agent with MCP tools."""
    print("=== Starting Fitness Manager with MCP Support ===")
    
    try:
        # Create agent with MCP tools
        agent, exit_stack = await create_fitness_manager_with_mcp()
        
        # Use async context manager to ensure proper cleanup
        async with exit_stack if exit_stack else asyncio.nullcontext():
            print("=== Agent created successfully ===")
            print(f"Agent tools: {[tool.name for tool in agent.tools]}")
            
            # Create session service
            session_service = InMemorySessionService()
            
            # Create runner
            runner = Runner(agent, session_service=session_service)
            
            print("=== Fitness Manager is ready! ===")
            print("Type 'quit' or 'exit' to stop the agent")
            print("-" * 50)
            
            # Interactive loop
            while True:
                try:
                    user_input = input("You: ").strip()
                    
                    if user_input.lower() in ['quit', 'exit', 'bye']:
                        print("Goodbye!")
                        break
                        
                    if not user_input:
                        continue
                    
                    print("Agent: ", end="", flush=True)
                    
                    # Run the agent
                    async for chunk in runner.run_stream(user_input):
                        if hasattr(chunk, 'content') and chunk.content:
                            print(chunk.content, end="", flush=True)
                    
                    print()  # New line after response
                    print("-" * 50)
                    
                except KeyboardInterrupt:
                    print("\nGoodbye!")
                    break
                except Exception as e:
                    print(f"Error: {e}")
                    continue
                    
    except Exception as e:
        print(f"Failed to create agent with MCP: {e}")
        print("Falling back to agent without MCP...")
        
        # Fallback to sync agent
        agent = FitnessManagerFactory.create_sync()
        session_service = InMemorySessionService()
        runner = Runner(agent, session_service=session_service)
        
        print("=== Fitness Manager is ready (without MCP) ===")
        print("Type 'quit' or 'exit' to stop the agent")
        print("-" * 50)
        
        # Interactive loop for fallback
        while True:
            try:
                user_input = input("You: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'bye']:
                    print("Goodbye!")
                    break
                    
                if not user_input:
                    continue
                
                print("Agent: ", end="", flush=True)
                
                # Run the agent
                async for chunk in runner.run_stream(user_input):
                    if hasattr(chunk, 'content') and chunk.content:
                        print(chunk.content, end="", flush=True)
                
                print()  # New line after response
                print("-" * 50)
                
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"Error: {e}")
                continue


def run_without_mcp():
    """Run the fitness manager agent without MCP tools (synchronous)."""
    print("=== Starting Fitness Manager without MCP Support ===")
    
    # Create agent without MCP
    agent = FitnessManagerFactory.create_sync()
    print(f"Agent tools: {[tool.name for tool in agent.tools]}")
    
    # This would need to be adapted based on how you want to run it
    print("=== Agent created successfully (sync mode) ===")
    print("Note: To run interactively, use the async version")


async def main():
    """Main entry point."""
    if len(sys.argv) > 1 and sys.argv[1] == "--no-mcp":
        run_without_mcp()
    else:
        await run_with_mcp()


if __name__ == "__main__":
    asyncio.run(main())


    Key Issues Fixed:

Proper Async Initialization: The main issue was that you were creating the agent synchronously (create_root_agent_sync()) but the MCP connection requires async initialization. You need to use create_root_agent_with_mcp() in an async context.
Exit Stack Management: The MCP connection returns an exit stack that needs to be properly managed using async with exit_stack: to ensure cleanup.
Error Handling: Better error handling for MCP connection failures with fallback to non-MCP agent.
Proper Tool Combination: Fixed how base tools and MCP tools are combined.

How to Use:
Option 1: Using the factory pattern
python# For async with MCP:
async def main():
    agent, exit_stack = await FitnessManagerFactory.create_with_mcp()
    async with exit_stack if exit_stack else asyncio.nullcontext():
        # Use your agent here
        pass

# For sync without MCP:
agent = FitnessManagerFactory.create_sync()
Option 2: Using the main runner
bash# Run with MCP support
python main_runner.py

# Run without MCP support
python main_runner.py --no-mcp
Option 3: Using ADK CLI
If you want to use the ADK CLI (adk run or adk web), you'll need to modify your agent file to properly handle the async initialization. The ADK CLI expects a synchronous agent definition, so you might need to handle the MCP initialization differently.
Common Issues:

NPX not found: Make sure Node.js and npm are installed
MCP server connection fails: Check your Supabase access token and network connectivity
Agent not showing MCP tools: Make sure you're using the async version and the exit stack is properly managed

The key insight is that MCP requires async initialization, so you need to structure your application to handle this properly. The synchronous version (root_agent = create_root_agent_sync()) will never have MCP tools because it can't perform the async MCP connection.