# Agent Pipeline Diagram

This document provides a visual representation of the agent pipeline in the Fitness Coach system, illustrating the flow of information and control between the main agents.

```text
┌────────────┐     ┌──────────────────────┐     ┌───────────────────┐
│            │     │                      │     │                   │
│   User     │◄───►│  Fitness Manager     │─────►│  Shared Session   │
│ (Frontend) │     │    (Root Agent)      │     │      State        │
│            │     │                      │     │  (User Profile,   │
└────────────┘     └───────────┬──────────┘     │   Results, etc.)  │
       ▲                       │                └───────────────────┘
       │                       │ Calls as Tool
       │                       ▼
       │           ┌──────────────────────┐
       │           │  Various Tools &     │
       │           │      Sub-Agents      │
       │           │  (Query Analyzer,    │
       │           │   User Profile,      │
       │           │    Data Tracker,     │
       │           │   Long Term Memory,  │
       │           │    Meal Planner,     │
       │           │   Workout Planner,   │
       │           │ Parallel Planners)   │
       │           └───────────┬──────────┘
       │                       │ Interacts with
       │                       │ Shared State
       │                       ▼
       │           ┌──────────────────────┐
       │           │  Report Synthesizer  │
       │           │       (Tool)       │
       │           └───────────┬──────────┘
       │                       │ Uses Shared State,
       │                       │ formats response
       │                       │
       │ Result                │
       └───────────────────────┘

```

**Explanation:**

1.  **User Interaction:** The user interacts with the system via the Frontend.
2.  **Fitness Manager (Root Agent):** The user's request is initially received by the `fitness_manager`, which is the main conversational agent. It directly uses various tools (`query_analyzer`, `check_missing_fields_tool`, `update_user_profile_tool`, `track_progress_tool`, `get_progress_report_tool`, `get_user_profile_tool`, `clear_user_profile_tool`, `search_long_term_memory_tool`) to understand the user's needs, gather necessary information, and interact with data. It also directly calls the `meal_planner`, `workout_planner`, and `parallel_planners` agents as tools to generate plans. Information is stored in the **Shared Session State**.
3.  **Shared Session State:** This central component holds user profile data, intermediate results (like meal and workout plans), and conversational context, accessible by different agents and tools within the same session.
4.  **Various Tools & Sub-Agents:** Based on the `fitness_manager`'s analysis and the user's request, it calls relevant tools and sub-agents directly. The planning agents (`meal_planner`, `workout_planner`, `parallel_planners`) access and update the Shared Session State with generated plans.
5.  **Report Synthesizer (Tool):** Once the necessary information is gathered and plans are generated, the `fitness_manager` calls the `report_synthesizer_tool`. This tool accesses the results from the Shared Session State and formats the final response for the user.
6.  **Result Back to Fitness Manager:** The output of the `report_synthesizer_tool` is returned to the `fitness_manager`.
7.  **Fitness Manager Presents Result:** The `fitness_manager` receives the formatted result and presents it to the user via the Frontend, completing the user's request and continuing the conversation. 