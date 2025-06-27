Connecting Your ADK AI Agent to Supabase: A Comprehensive Guide
Connecting your custom AI agent, built with the Google Agent Development Kit (ADK), to a powerful and easy-to-use database like Supabase is a critical step in creating a robust and personalized user experience. This guide will walk you through the best practices and recommended methods for achieving this integration, enabling your agent to store user profiles, save personalized meal and workout plans, and deliver a more dynamic and stateful service.
The optimal approach for connecting your ADK agent to Supabase is by leveraging ADK's "Tool" functionality in conjunction with the supabase-py Python client library. This method allows for a clean separation of concerns, enhances security, and aligns with the code-first philosophy of the Agent Development Kit.
The Core Concept: ADK Tools for Database Interaction
In the ADK framework, a "Tool" is a Python function that you make available to your AI agent.[1][2] The agent, powered by a large language model (LLM), can then decide to call these tools to perform specific actions, such as querying a database, calling an external API, or accessing local files.[1][3] This is the fundamental mechanism for extending your agent's capabilities beyond its core conversational abilities.
For your meal and workout planning agent, you will create Python functions that handle all interactions with your Supabase database. These functions will then be registered as tools that your ADK agent can utilize.
Step-by-Step Integration Guide
Here’s a detailed breakdown of how to connect your ADK agent to Supabase:
1. Set Up Your Supabase Project
Before you begin coding, ensure your Supabase project is ready:
Create a Supabase Project: If you haven't already, create a new project on the Supabase website.
Design Your Database Schema: In the Supabase dashboard, use the table editor to create the necessary tables. For your use case, you might have:
A users table to store profile information like user_id, height, weight, goals, etc.
A meal_plans table to store the generated meal plans, linked to a user_id.
A workout_plans table, also associated with a user_id.
Obtain Your API Credentials: Navigate to the "API" settings in your Supabase project to find your Project URL and anon and service_role keys. For server-side operations within your ADK agent, it is recommended to use the service_role key, but be sure to handle it securely.
2. Install the supabase-py Library
The supabase-py library is the official Python client for Supabase and provides a convenient way to interact with your Supabase backend. Install it in your project's Python environment:
Generated bash
pip install supabase
Use code with caution.
Bash
You will also need to have the google-adk library installed.[4]
3. Securely Manage Your Credentials
Never hardcode your Supabase URL and API keys directly in your agent's code. Instead, use environment variables. The ADK framework is designed to work seamlessly with .env files.
Create a .env file in the root of your ADK project and add your Supabase credentials:
Generated code
SUPABASE_URL="your-supabase-project-url"
SUPABASE_KEY="your-supabase-service-role-key"
Use code with caution.
You can then load these variables in your Python code using a library like python-dotenv.
4. Create Database Interaction Tools
Now, you will write the Python functions that will serve as your agent's tools for interacting with Supabase. These functions will use the supabase-py library to perform CRUD (Create, Read, Update, Delete) operations.
Here are some example tool functions for your meal and workout planner agent:
Generated python
import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize the Supabase client
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

def save_user_profile(user_id: str, height: int, weight: int, goals: str) -> str:
    """Saves a new user's profile information to the database."""
    try:
        data, count = supabase.table('users').insert({
            "user_id": user_id,
            "height": height,
            "weight": weight,
            "goals": goals
        }).execute()
        return "User profile saved successfully."
    except Exception as e:
        return f"Error saving user profile: {e}"

def get_user_profile(user_id: str) -> dict:
    """Retrieves a user's profile information from the database."""
    try:
        data, count = supabase.table('users').select('*').eq('user_id', user_id).execute()
        if data and len(data[1]) > 0:
            return data[1][0]
        return None
    except Exception as e:
        print(f"Error getting user profile: {e}")
        return None

def save_meal_plan(user_id: str, meal_plan: dict) -> str:
    """Saves a user's confirmed meal plan to the database."""
    try:
        data, count = supabase.table('meal_plans').insert({
            "user_id": user_id,
            "plan_details": meal_plan
        }).execute()
        return "Meal plan saved successfully."
    except Exception as e:
        return f"Error saving meal plan: {e}"
Use code with caution.
Python
5. Register the Tools with Your ADK Agent
Once you have defined your database interaction functions, you need to make them available to your ADK agent by wrapping them as FunctionTool and passing them to the agent's tools parameter during initialization.
Here is how you would define your agent and register the tools:
Generated python
from google.adk.agents import Agent
from google.adk.tools import FunctionTool

# ... (import your database functions: save_user_profile, get_user_profile, save_meal_plan)

# Create a list of your database tools
database_tools = [
    FunctionTool(save_user_profile),
    FunctionTool(get_user_profile),
    FunctionTool(save_meal_plan),
]

# Define your ADK agent
meal_planner_agent = Agent(
    name="meal_planner_agent",
    model="gemini-1.5-flash",  # Or your preferred model
    instructions="You are an AI assistant that helps users create meal and workout plans. Use the available tools to save and retrieve user information and plans.",
    tools=database_tools,
)
Use code with caution.
Python
6. Interacting with the Agent
Now, when you run your ADK agent, it will have the ability to call the functions you've provided. For example, a user interaction might go like this:
User: "Hi, I'm a new user. My height is 180cm and I weigh 75kg. My goal is to build muscle."
The LLM powering your agent will understand the user's intent and the provided information. It will then determine that it needs to call the save_user_profile tool and will extract the necessary arguments (user_id, height, weight, goals) from the user's message. The ADK will execute the function, and the user's profile will be saved to your Supabase database.
Similarly, once a meal plan is generated and the user confirms it, you can prompt the agent to save it:
User: "This meal plan looks great! Please save it for me."
The agent will then call the save_meal_plan tool with the user's ID and the meal plan details.
Managing User State and Sessions
A key advantage of using a database is the ability to maintain user state across different sessions. The ADK provides mechanisms for session management. By default, it uses an in-memory session service, but this can be customized.[5]
By storing a unique user_id for each user in your Supabase database, you can retrieve their profile information at the beginning of a new conversation. This allows your agent to have a "memory" of the user, leading to more personalized and context-aware interactions. You can design your agent's initial prompt to always first check if a user profile exists by calling the get_user_profile tool.
Conclusion
Connecting your ADK AI agent to Supabase through the use of ADK Tools and the supabase-py library is a flexible, secure, and scalable solution. This approach allows you to build sophisticated, stateful AI applications that can store and retrieve user-specific data, paving the way for highly personalized and effective meal and workout planning assistants. By following the steps outlined in this guide and referencing the official ADK and supabase-py documentation, you can successfully bridge the gap between your intelligent agent and a robust database backend.