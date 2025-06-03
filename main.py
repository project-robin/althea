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

# Export the root_agent which is now a BaseAgent instance
# No function call needed, since agent.py now exports an instance directly
agent = root_agent