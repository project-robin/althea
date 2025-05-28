# Althea - AI Fitness Coach

A multi-agent AI fitness and nutrition coaching system built with Google's Agent Development Kit (ADK).

## Overview

This system features a flexible architecture centered around a primary "Manager" agent that intelligently orchestrates specialized "Expert" agents and tools to provide comprehensive fitness and nutrition guidance:

- **Fitness Manager Agent (Main Agent)**: Serves as the user's primary interface. It analyzes user requests to determine their specific needs (meal plan, workout plan, both, progress tracking, or general advice). Based on this analysis and collected user information, it dynamically delegates the task to the appropriate specialized agent or workflow, and synthesizes the final response for the user. It also manages user profile data and long-term memory.
- **Meal Plan Agent (Expert Agent)**: A specialized agent focused on generating personalized meal plans based on user goals, preferences, and dietary restrictions.
- **Workout Plan Agent (Expert Agent)**: A specialized agent focused on creating customized workout routines based on user fitness level, goals, and available equipment.
- **Parallel Planners (Workflow Agent)**: An orchestration agent used by the Manager Agent to run the Meal Plan Agent and Workout Plan Agent concurrently when a user requests both types of plans. This improves efficiency for combined requests.
- **Report Synthesizer Tool**: A dedicated tool used by the Manager Agent to combine the results from the Meal Plan Agent and Workout Plan Agent into a single, comprehensive report when both plans are generated.

This architecture allows for efficient handling of diverse user requests, leveraging parallel execution where beneficial, and maintaining a clear separation of concerns among specialized agents.

## Features

- Personalized meal plan creation
- Custom workout routine development
- Progress tracking and analysis
- Goal setting and adherence monitoring
- Comprehensive nutrition and fitness advice

## Installation

1. Ensure you have Python 3.10+ and Poetry installed
2. Clone this repository
3. Install dependencies:

```bash
poetry install
```

4. Create a `.env` file with your API keys (see `.env.example` once available)

## Usage

Run the fitness coach agent:

```bash
poetry run adk run .
```

Or use the ADK web UI:

```bash
poetry run adk web
```

Then select the Fitness Manager agent from the dropdown.

## Project Structure

```
fitness-coach/
├── fitness_coach/
│   ├── __init__.py
│   ├── agent.py  # Main Manager Agent
│   ├── prompt.py # Manager Agent prompts
│   ├── tools/    # Manager Agent tools
│   └── sub_agents/
│       ├── meal_planner/
│       │   ├── agent.py
│       │   ├── prompt.py
│       │   └── tools/
│       └── workout_planner/
│           ├── agent.py
│           ├── prompt.py
│           └── tools/
├── deployment/
├── eval/
├── tests/
├── .env.example
├── pyproject.toml
└── README.md
```

## Acknowledgements

Built with Google's [Agent Development Kit (ADK)](https://github.com/google/adk-python)