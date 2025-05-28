"""
Main entry point for the Fitness Coach application.

This module exports the main fitness_manager agent as the default agent
for the ADK web interface and CLI.
"""

from fitness_coach.agent import fitness_manager
from fitness_coach.agent import root_agent

# Export the fitness_manager as the default agent
agent = fitness_manager 