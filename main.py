"""
Main entry point for the Fitness Coach application.

This module exports the main fitness_manager agent as the default agent
for the ADK web interface and CLI.
"""

"""
Main entry point for the Fitness Coach application.

This module exports the root_agent function as the default agent
for the ADK web interface and CLI.
"""
from fitness_coach.agent import root_agent
import asyncio
from contextlib import AsyncExitStack

# Export the root_agent which is now a BaseAgent instance
# No function call needed, since agent.py now exports an instance directly
agent = root_agent

async def get_agent_instance():
    """Asynchronously creates and returns the agent instance and its exit stack."""
    async with AsyncExitStack() as es:
        agent, _ = await root_agent()  # Unpack only the agent, ignore the None exit_stack
        # No need to push supabase_exit_stack as it's no longer returned/used
        return agent, es

# The 'agent' variable is expected to be an instance of BaseAgent, not a coroutine.
# We will create a coroutine that returns the agent, and the ADK runner will handle awaiting it.
# To be compatible with ADK's expectation, we create a function that returns the agent and its exit stack.
# The ADK runner will call this function and manage the lifecycle.
agent = get_agent_instance