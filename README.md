# Althea - AI Fitness Coach

A multi-agent AI fitness and nutrition coaching system built with Google's Agent Development Kit (ADK).

## Overview

This system consists of a primary "Manager" agent and two specialized "Expert" agents to provide comprehensive fitness and nutrition guidance:

- **Fitness Manager Agent (Main Agent)**: Acts as the user's primary interface, delegating tasks to expert agents and synthesizing information.
- **Meal Plan Agent (Expert Agent)**: Specializes in creating personalized meal plans based on user goals and preferences.
- **Workout Plan Agent (Expert Agent)**: Specializes in creating personalized workout routines based on fitness level and goals.

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