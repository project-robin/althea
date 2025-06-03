**# Calorie Tracking and Meal Suggestion Implementation Plan**

This document outlines the phase-wise plan to add calorie tracking and meal suggestion features to the AI Fitness Coach agent system, including integrating with a PostgreSQL database via a fastmcp MCP.

✅ **Phase 1: Set up FastMCP for PostgreSQL Interaction**

*   **Goal:** Create a fastmcp MCP that acts as an interface to the PostgreSQL database for calorie tracking data.
*   **Steps:**
    1.  Create a new directory `fitness_coach/mcp/`.
    2.  Create a new Python file `fitness_coach/mcp/database_mcp.py`.
    3.  Install necessary dependencies: `fastmcp` and a PostgreSQL adapter (e.g., `asyncpg` or `psycopg2`) using Poetry. Update `pyproject.toml`.
    4.  In `database_mcp.py`, initialize a `FastMCP` instance.
    5.  Implement asynchronous functions for database operations:
        *   `connect_db()`: Establishes a connection to the PostgreSQL database.
        *   `close_db()`: Closes the database connection.
        *   `create_tables()`: Creates necessary tables (e.g., `food_items`, `user_food_entries`) if they don't exist.
    6.  Define fastmcp tools using the `@mcp.tool()` decorator in `database_mcp.py`:
        *   `get_food_info(food_name: str) -> dict`: Retrieves calorie and macronutrient information for a given food item from the `food_items` table.
        *   `add_user_food_entry(user_id: str, food_name: str, quantity: float, calories: float, protein: float, carbs: float, fat: float, date: str)`: Records a user's food intake in the `user_food_entries` table.
        *   `get_user_daily_calories(user_id: str, date: str) -> float`: Calculates the total calorie intake for a user on a specific date.
        *   `get_user_daily_macros(user_id: str, date: str) -> dict`: Calculates the total macronutrient intake for a user on a specific date.
    7.  Include logic to run the fastmcp server, likely using `mcp.run()` with an appropriate transport (e.g., STDIO for local development/integration with ADK agent).
    8.  Add environment variables for database connection details (connection string, credentials) and document them in `.env.example`.
    9.  Write basic tests for the MCP tools.
*   **Documentation Reference:**
    *   fastmcp documentation: `getting-started/quickstart.mdx`, `servers/fastmcp.mdx`, `servers/tools.mdx`.
    *   ADK documentation: `Toolbox Tools for Databases` mentioned in `Tools and Capabilities`.

✅ **Phase 2: Integrate MCP Client into Fitness Manager Agent**

*   **Goal:** Modify the main fitness manager agent to interact with the database MCP to track calories.
*   **Steps:**
    1.  In `fitness_coach/agent.py`, import `fastmcp.Client`.
    2.  Instantiate a `fastmcp.Client` to connect to the running database MCP. Configure the client with the MCP server's transport details.
    3.  Modify the agent's instruction and description in `fitness_coach/prompt.py` to include the calorie tracking capability.
    4.  Enhance the agent's processing logic (likely within the main agent class in `agent.py`) to:
        *   Recognize user input related to food intake (e.g., "I ate two apples", "Had a slice of pizza").
        *   Parse the food item(s) and quantity from the user's message.
        *   Call the `get_food_info` MCP tool for each identified food item to get calorie/macro data.
        *   Calculate the total calories and macronutrients for the reported meal.
        *   Call the `add_user_food_entry` MCP tool to record the meal in the database.
        *   Provide a confirmation message to the user about the logged entry.
*   **Documentation Reference:**
    *   fastmcp documentation: `clients/client.mdx`, `clients/transports.mdx`.
    *   ADK documentation: `Agent Fundamentals`, `Tools and Capabilities` (specifically using other agents or MCPs as tools).

✅ **Phase 3: Implement Calorie Limit Check and Meal Suggestions**

*   **Goal:** Add logic to the fitness manager agent to check calorie limits and provide meal suggestions or warnings.
*   **Steps:**
    1.  In `fitness_coach/agent.py`, retrieve the user's daily calorie goal. This information is assumed to be available (e.g., stored in the ADK session state after onboarding).
    2.  After adding a new food entry (in Phase 2), call the `get_user_daily_calories` MCP tool to get the updated daily intake.
    3.  Compare the current daily calorie intake with the user's goal.
    4.  Based on the comparison:
        *   If the user is approaching or exceeding their calorie limit, inform them.
        *   If the user reports an unhealthy meal (this will require the agent to classify the meal's healthiness, potentially using its LLM capabilities or information from the `food_items` table), provide suggestions for healthier alternatives or advise on portion control.
    5.  Refine the agent's prompt (`fitness_coach/prompt.py`) to guide its response generation for calorie tracking feedback and meal suggestions.
    6.  Add logic to the agent to handle user confirmation before storing the food entry (if required by your desired workflow).
*   **Documentation Reference:**
    *   ADK documentation: `LLM Agents (LlmAgent, Agent)`, `Conversational Context and Runtime (Session, State, and Memory)`.

✅ **Phase 4: Refine and Test**

*   **Goal:** Ensure the implemented features are robust, production-ready, and well-tested I'm properly implemented according to the official document.
*   **Steps:**
    1.  Write comprehensive unit and integration tests for the database MCP and the fitness manager agent's new functionalities.
    2.  Perform end-to-end testing of the calorie tracking and suggestion features within the ADK agent system.
    3.  Review error handling in both the MCP and the agent to ensure graceful failure and informative error messages.
    4.  Optimize database queries within the MCP for performance.
    5.  Consider how to handle edge cases (e.g., unknown food items, ambiguous user input).Also read the adk-Docs to see can be implement callbacks to mitigat  Ambiguous user input or bad input by user
    6.  Update the `README.md` with instructions on setting up and running the database MCP and the agent with the new features. 