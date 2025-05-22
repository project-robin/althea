# Fitness Coach API and Frontend Integration

This README provides instructions for setting up and running the FastAPI backend and Streamlit frontend for the Fitness Coach multi-agent system.

## Overview

The system consists of:

1. **FastAPI Backend**: Exposes the ADK agents through HTTP endpoints
2. **Streamlit Frontend**: Provides a simple, user-friendly interface for interacting with the fitness coach

## Prerequisites

- Python 3.10+ installed
- Google API key or Vertex AI access configured

## Installation

1. Clone this repository
2. Set up a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Ensure your `.env` file is configured with API keys (see `.env.example`)

## Running the Backend

Run the FastAPI backend with:

```bash
python api.py
```

The backend will be available at:
- REST API: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- ADK Web UI: http://localhost:8000/dev-ui

## Running the Frontend

Run the Streamlit frontend with:

```bash
streamlit run frontend.py
```

The frontend will be available at http://localhost:8501

## API Endpoints

The API server exposes the following endpoints:

- `/health`: Health check endpoint
- `/agent-info`: Get information about available agents
- `/generate-session-id`: Generate a unique session ID
- `/apps/{app_name}/users/{user_id}/sessions/{session_id}`: Create a new session
- `/run`: Send a message to an agent and receive a response
- `/run_sse`: Stream responses from an agent

## Frontend Features

The Streamlit frontend provides:

- A chat interface for interacting with the fitness coach
- A form to enter your fitness profile
- Session management capabilities

## Usage Flow

1. Create a session
2. Fill out your fitness profile
3. Chat with the fitness coach to receive personalized meal plans and workout routines

## Development Notes

- The backend uses ADK's FastAPI integration to expose the agents
- The frontend communicates with the backend via HTTP requests
- User sessions are stored in an SQLite database by default

## Advanced Configuration

For production deployment, consider:

- Using a more robust database (PostgreSQL, etc.)
- Restricting CORS origins
- Setting up proper authentication
- Deploying behind a reverse proxy (Nginx, etc.) 