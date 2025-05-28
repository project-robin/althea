"""
FastAPI server for fitness coach agents.

This module exposes the fitness coach agents via FastAPI endpoints.
It allows frontend applications to interact with agents through HTTP requests.
"""

import os
import sys
import uuid
import socket
import json
from typing import Dict, List, Any, Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel
from google.adk.cli.fast_api import get_fast_api_app
import uvicorn

# Load environment variables
load_dotenv()

# Set up paths
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
AGENT_DIR = os.path.join(BASE_DIR, "fitness_coach")  # Path to agent directory
SESSION_DB_URL = f"sqlite:///{os.path.join(BASE_DIR, 'sessions.db')}"

# Create the FastAPI app using ADK's helper
app = get_fast_api_app(
    agent_dir=AGENT_DIR,
    session_db_url=SESSION_DB_URL,
    allow_origins=["*"],  # For development only, restrict in production
    web=True,  # Enable the ADK Web UI at /dev-ui
)

# Add CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development - restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define Pydantic models for request/response types
class UserProfile(BaseModel):
    name: str
    age: int
    gender: str
    weight: float
    height: float
    fitness_level: str
    goals: List[str]
    dietary_restrictions: Optional[List[str]] = None
    preferred_workout_days: Optional[List[str]] = None
    health_conditions: Optional[List[str]] = None

class Message(BaseModel):
    role: str
    parts: List[Dict[str, Any]]

class SessionRequest(BaseModel):
    app_name: str
    user_id: str 
    session_id: str
    new_message: Message

class SessionResponse(BaseModel):
    session_id: str
    events: List[Dict[str, Any]]

class FormattedResponseData(BaseModel):
    text: str
    structured_data: Optional[Dict[str, Any]] = None

# Custom middleware to intercept and modify responses
@app.middleware("http")
async def process_formatted_responses(request: Request, call_next):
    # Process the request normally
    response = await call_next(request)
    
    # Check if this is a response from the /run endpoint and is successful
    if request.url.path == "/run" and response.status_code == 200:
        try:
            # Check if the response is a StreamingResponse (common for ADK)
            # We need to consume the body to access it
            if hasattr(response, "body"):
                body = await response.body()
                try:
                    # Parse the response body as JSON (assuming it's a list of events)
                    events = json.loads(body)
                    print(f"Successfully parsed JSON response with {len(events)} events")
                    
                    # Process each event looking for model content with tool results
                    for i, event in enumerate(events):
                        # Check if the event is from the model and has content parts
                        if event.get("content", {}).get("role") == "model":
                            parts = event.get("content", {}).get("parts", [])
                            print(f"Event {i+1} has {len(parts)} parts")

                            # Check for function call results in the event
                            # ADK puts tool results in parts with a 'functionResponse' key
                            for part_idx, part in enumerate(parts):
                                function_response = part.get("functionResponse")
                                if function_response:
                                    tool_name = function_response.get("name")
                                    tool_output = function_response.get("response", {}).get("content")

                                    # Check if this is the response_formatter tool and it returned content
                                    if tool_name == "response_formatter" and tool_output:
                                        try:
                                            # The structured data is expected to be a JSON string within the tool output content
                                            structured_data = json.loads(tool_output)
                                            print(f"Found structured data from {tool_name} in event {i+1}, part {part_idx+1}")
                                                
                                            # Find the preceding text part for this event to attach structured data
                                            # Assuming the text part comes before the tool response part in the list
                                            for text_part_idx in range(part_idx):
                                                 if "text" in parts[text_part_idx]:
                                                    # Add the structured data to the text part
                                                    parts[text_part_idx]["structured_data"] = structured_data.get("formatted_response", {}).get("structured_data") # Extract the inner structured_data
                                                    print(f"Attached structured data to text part {text_part_idx+1}")
                                                    break # Assume one text part per structured data

                                        except json.JSONDecodeError as e:
                                            print(f"Error parsing structured data JSON from tool output: {e}")
                                        except Exception as e:
                                            print(f"Error processing tool output: {str(e)}")
                    
                    # Return the modified response as JSON
                    return Response(
                        content=json.dumps(events),
                        status_code=response.status_code,
                        headers=dict(response.headers),
                        media_type="application/json"
                    )

                except json.JSONDecodeError as e:
                    print(f"Error parsing response body as JSON: {e}")
                    # If the response isn't valid JSON, return it as is
                    return response
            else:
                print(f"Skipping middleware processing for response type: {type(response).__name__} (no body)")

        except Exception as e:
            print(f"Error in middleware processing response: {str(e)}")
            import traceback
            traceback.print_exc()
    
    # Return original response for streaming responses or other endpoints
    # Note: This middleware might need further refinement for true SSE streaming
    # if the frontend expects incremental updates rather than a single JSON list.
    return response

# Additional endpoints for our fitness coach app
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

@app.get("/agent-info")
async def agent_info():
    """Get information about available agents."""
    # Import agents from fitness_coach
    from fitness_coach.agent import fitness_manager
    from fitness_coach.sub_agents.meal_planner.agent import meal_planner
    from fitness_coach.sub_agents.workout_planner.agent import workout_planner
    
    return {
        "main_agent": {
            "name": fitness_manager.name,
            "description": fitness_manager.description,
            "model": fitness_manager.model,
        },
        "sub_agents": [
            {
                "name": meal_planner.name,
                "description": meal_planner.description,
                "model": meal_planner.model,
            },
            {
                "name": workout_planner.name,
                "description": workout_planner.description,
                "model": workout_planner.model,
            }
        ]
    }

@app.get("/generate-session-id")
async def generate_session_id():
    """Generate a unique session ID for new users."""
    return {"session_id": str(uuid.uuid4())}

# The main run endpoint is already provided by ADK's get_fast_api_app()
# at /run and /run_sse for streaming

def find_available_port(start_port, max_attempts=10):
    """Find an available port starting from start_port."""
    current_port = start_port
    for _ in range(max_attempts):
        try:
            # Try to create a socket binding to check if port is available
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('0.0.0.0', current_port))
                return current_port
        except OSError:
            # Port is not available, try the next one
            print(f"Port {current_port} is in use, trying {current_port + 1}")
            current_port += 1
    
    # If we get here, we couldn't find an available port
    raise RuntimeError(f"Could not find an available port after {max_attempts} attempts")

if __name__ == "__main__":
    default_port = int(os.getenv("PORT", "8000"))
    host = os.getenv("HOST", "0.0.0.0")
    
    try:
        port = find_available_port(default_port)
        print(f"Starting FastAPI server on http://{host}:{port}")
        uvicorn.run(app, host=host, port=port)
    except RuntimeError as e:
        print(f"Error: {e}")
        sys.exit(1) 