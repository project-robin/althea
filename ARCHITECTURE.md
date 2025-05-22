# Fitness Coach System Architecture

This document describes the architecture of the Fitness Coach multi-agent system, focusing on how the agents communicate with the frontend through the FastAPI backend.

## System Overview

```
┌───────────────┐      ┌─────────────────┐      ┌────────────┐
│               │      │                 │      │            │
│  Streamlit    │◄────►│  FastAPI        │◄────►│ ADK Agents │
│  Frontend     │      │  Backend        │      │            │
│               │      │                 │      │            │
└───────────────┘      └─────────────────┘      └────────────┘
                                                      │
                                                      ▼
                                               ┌────────────────┐
                                               │                │
                                               │  LLM Provider  │
                                               │  (Gemini)      │
                                               │                │
                                               └────────────────┘
```

## Components

### 1. ADK Agents

The system uses Google's Agent Development Kit (ADK) to define a hierarchical multi-agent system:

- **Fitness Manager Agent** (root_agent): Handles user interaction, delegates tasks to expert agents, and synthesizes responses
- **Meal Planner Agent**: Creates personalized meal plans based on user goals and preferences
- **Workout Planner Agent**: Creates personalized workout routines based on fitness level and goals

Each agent has:
- A specific instruction set that defines its behavior
- A set of tools that it can use to perform tasks
- Access to user data through shared state

### 2. FastAPI Backend

The FastAPI backend serves as an interface between the frontend and the ADK agents. It:

- Uses ADK's `get_fast_api_app()` to expose agent functionality through HTTP endpoints
- Adds custom endpoints for health checks, agent information, and session management
- Handles session creation and management with SQLite database storage
- Processes requests and responses, including streaming responses via Server-Sent Events (SSE)

Key endpoints:
- `/apps/{app_name}/users/{user_id}/sessions/{session_id}`: Create a new session
- `/run`: Send a message to an agent and receive a response
- `/run_sse`: Stream responses from an agent
- `/health`: Health check endpoint
- `/agent-info`: Get information about available agents
- `/generate-session-id`: Generate a unique session ID

### 3. Streamlit Frontend

The Streamlit frontend provides a user-friendly interface for interacting with the fitness coach. It:

- Creates and manages user sessions
- Collects user profile information through forms
- Displays chat messages between the user and the fitness coach
- Formats agent responses for easy readability

## Communication Flow

### 1. Session Creation

```
┌───────────────┐      ┌─────────────────┐      ┌────────────┐
│  Frontend     │      │  Backend        │      │  Agents    │
└───────┬───────┘      └────────┬────────┘      └─────┬──────┘
        │                       │                     │
        │ Create Session        │                     │
        │───────────────────────►                     │
        │                       │                     │
        │                       │ Initialize Session  │
        │                       │────────────────────►│
        │                       │                     │
        │                       │ Session Created     │
        │                       │◄────────────────────│
        │                       │                     │
        │ Session ID            │                     │
        │◄───────────────────────                     │
        │                       │                     │
```

### 2. Sending Messages

```
┌───────────────┐      ┌─────────────────┐      ┌────────────┐      ┌────────────┐
│  Frontend     │      │  Backend        │      │ Main Agent │      │Sub Agents  │
└───────┬───────┘      └────────┬────────┘      └─────┬──────┘      └─────┬──────┘
        │                       │                     │                   │
        │ Send Message          │                     │                   │
        │───────────────────────►                     │                   │
        │                       │                     │                   │
        │                       │ Process Message     │                   │
        │                       │────────────────────►│                   │
        │                       │                     │                   │
        │                       │                     │ Delegate Task     │
        │                       │                     │──────────────────►│
        │                       │                     │                   │
        │                       │                     │ Return Results    │
        │                       │                     │◄──────────────────│
        │                       │                     │                   │
        │                       │ Return Response     │                   │
        │                       │◄────────────────────│                   │
        │                       │                     │                   │
        │ Response Events       │                     │                   │
        │◄───────────────────────                     │                   │
        │                       │                     │                   │
```

## Data Flow

### User Profile Data

1. User enters profile data in the frontend
2. Frontend sends profile data to the backend as a message
3. Backend passes the message to the fitness manager agent
4. The fitness manager agent:
   - Extracts and processes profile information
   - Updates user profile in the shared state
   - Delegates specialized tasks to expert agents as needed

### Agent Responses

1. Agent generates a response (which may include function calls)
2. Function calls are executed and produce results
3. Results are incorporated into the agent's response
4. Response is sent back to the frontend as a series of events
5. Frontend processes and displays these events

## State Management

The system manages state across sessions:

1. **Session State**: ADK maintains session state between interactions
2. **User Profile**: The user's fitness profile is stored in session state
3. **Progress Data**: User progress is tracked and stored in session state
4. **Conversation History**: The chat history is maintained in both the frontend and backend

## Error Handling

The system implements error handling at multiple levels:

1. **Frontend**: Catches and displays API request errors
2. **Backend**: Validates requests and provides appropriate HTTP error responses
3. **Agents**: Handle tool execution errors and provide graceful fallbacks

## Scalability Considerations

For scaling beyond the MVP:

1. **Database**: Replace SQLite with a more robust database (PostgreSQL, etc.)
2. **Authentication**: Add proper user authentication and authorization
3. **Caching**: Implement response caching for common queries
4. **Load Balancing**: Deploy multiple instances behind a load balancer

## Security Considerations

1. **API Keys**: Never expose API keys in the frontend
2. **CORS**: Restrict CORS to known origins in production
3. **Input Validation**: Validate all user inputs before processing
4. **Rate Limiting**: Implement rate limiting to prevent abuse

## Extending the System

To extend the system with new capabilities:

1. **Add New Tools**: Create new tools in the appropriate agent's tools directory
2. **Add New Sub-Agents**: Create specialized agents for new domains
3. **Enhance Frontend**: Add new UI components to support new features 