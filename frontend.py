"""
Streamlit frontend for the Fitness Coach multi-agent system.

This is a simplified MVP frontend that connects to our FastAPI backend
which exposes the fitness coach agents.
"""

import os
import uuid
import json
import requests
import re
import streamlit as st
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
APP_NAME = "fitness_coach"  # Name of our agent app in ADK

# Page setup
st.set_page_config(
    page_title="AI Fitness Coach",
    page_icon="💪",
    layout="wide"
)

# Helper functions for structured plan rendering
def render_workout_plan(text):
    """Parse and render a workout plan in a structured, visual format."""
    # Check if this is a workout plan response
    if not any(keyword in text.lower() for keyword in ["workout plan", "training frequency", "workout-by-workout"]):
        return None
    
    # Try to parse the main sections
    sections = {}
    current_section = None
    
    # Common section patterns in workout plans
    section_patterns = [
        "Overall Program Structure:",
        "Workout-by-Workout Breakdown:",
        "Warm-up",
        "Workout A",
        "Workout B",
        "Workout C",
        "Cool-down",
        "General Guidance:",
        "Progression:",
        "Tracking Progress:",
        "Listen to Your Body:"
    ]
    
    lines = text.split('\n')
    for line in lines:
        # Check if this line starts a new section
        is_section_header = False
        for pattern in section_patterns:
            if line.strip().startswith(pattern):
                current_section = pattern.rstrip(':')
                sections[current_section] = []
                is_section_header = True
                break
        
        # Add content to the current section
        if current_section and not is_section_header:
            sections[current_section].append(line.strip())
    
    if not sections:
        return None  # Not a parseable workout plan
    
    # Render as a structured UI
    st.subheader("📋 Your Personalized Workout Plan")
    
    # Render program structure in a highlighted box
    if "Overall Program Structure" in sections:
        with st.expander("Program Overview", expanded=True):
            structure_text = "\n".join(sections["Overall Program Structure"])
            structure_items = re.findall(r'([^:]+):\s*([^•]+)', structure_text)
            
            # Create a clean formatted version of the structure
            for item, description in structure_items:
                st.markdown(f"**{item.strip()}**: {description.strip()}")
    
    # Render workouts in tabs
    workout_keys = [k for k in sections.keys() if k.startswith("Workout")]
    if workout_keys:
        tabs = st.tabs([f"{workout}" for workout in workout_keys])
        
        for i, workout_key in enumerate(workout_keys):
            with tabs[i]:
                workout_content = "\n".join(sections[workout_key])
                
                # Extract exercises using regex
                exercises = re.findall(r'([^:]+):\s*(\d+[^\.]+)[^\n]*\n\s*([^:]+)', workout_content)
                
                if exercises:
                    for name, sets_reps, cue in exercises:
                        with st.container():
                            cols = st.columns([3, 2])
                            with cols[0]:
                                st.markdown(f"**{name.strip()}**")
                                st.caption(f"{sets_reps.strip()}")
                            with cols[1]:
                                st.markdown(f"💡 *{cue.strip()}*")
                            st.divider()
                else:
                    # Fallback if parsing fails
                    st.write(workout_content)
    
    # Render guidance sections in expandable sections
    guidance_sections = ["General Guidance", "Progression", "Tracking Progress", "Listen to Your Body"]
    for section in guidance_sections:
        if section in sections:
            with st.expander(section):
                st.write("\n".join(sections[section]))
    
    return True  # Successfully rendered

def render_meal_plan(text):
    """Parse and render a meal plan in a structured, visual format."""
    # Check if this is a meal plan response
    if not any(keyword in text.lower() for keyword in ["meal plan", "calori", "macronutrient"]):
        return None
    
    # Try to parse the main sections
    sections = {}
    current_section = None
    
    # Common section patterns in meal plans
    section_patterns = [
        "Overall Plan Summary:",
        "Meal-by-Meal Breakdown:",
        "Breakfast",
        "Mid-Morning Snack",
        "Lunch",
        "Evening Snack",
        "Dinner",
        "Post-Dinner",
        "General Guidance:"
    ]
    
    lines = text.split('\n')
    for line in lines:
        # Check if this line starts a new section
        is_section_header = False
        for pattern in section_patterns:
            if pattern in line:
                current_section = pattern.rstrip(':')
                sections[current_section] = []
                is_section_header = True
                break
        
        # Special handling for meal times with parentheses
        meal_time_match = re.search(r'([^:]+)\s*\(([^)]+)\):', line)
        if meal_time_match:
            meal_name = meal_time_match.group(1).strip()
            meal_time = meal_time_match.group(2).strip()
            current_section = meal_name
            sections[current_section] = [f"Time: {meal_time}"]
            is_section_header = True
        
        # Add content to the current section
        if current_section and not is_section_header:
            sections[current_section].append(line.strip())
    
    if not sections:
        return None  # Not a parseable meal plan
    
    # Render as a structured UI
    st.subheader("🍽️ Your Personalized Meal Plan")
    
    # Render summary in a highlighted box
    if "Overall Plan Summary" in sections:
        with st.expander("Plan Overview", expanded=True):
            summary_text = "\n".join(sections["Overall Plan Summary"])
            
            # Extract calorie and macro information
            calories_match = re.search(r'Total Daily Calories:\s*(\d+)', summary_text)
            macros_match = re.findall(r'([^:]+):\s*([^(]+)\(([^)]+)\)', summary_text)
            
            if calories_match:
                st.markdown(f"**Daily Calories:** {calories_match.group(1)} kcal")
            
            if macros_match:
                st.markdown("**Macronutrients:**")
                cols = st.columns(len(macros_match))
                for i, (name, amount, percentage) in enumerate(macros_match):
                    with cols[i]:
                        st.metric(
                            label=name.strip(),
                            value=amount.strip(),
                            delta=percentage.strip()
                        )
    
    # Render meals in a timeline view
    meal_keys = ["Breakfast", "Mid-Morning Snack", "Lunch", "Evening Snack", "Dinner", "Post-Dinner"]
    meal_keys = [k for k in meal_keys if k in sections]
    
    if meal_keys:
        for meal_key in meal_keys:
            meal_content = "\n".join(sections[meal_key])
            
            with st.container():
                st.markdown(f"### {meal_key}")
                
                # Extract meal details using regex
                dish_match = re.search(r'Dish:\s*([^\n]+)', meal_content)
                calories_match = re.search(r'Calories:\s*([^\n]+)', meal_content)
                macros_match = re.search(r'Carbs:\s*([^,]+),\s*Protein:\s*([^,]+),\s*Fat:\s*([^\n]+)', meal_content)
                prep_match = re.search(r'Preparation:\s*([^\n]+)', meal_content)
                subst_match = re.search(r'Substitution:\s*([^\n]+)', meal_content)
                
                cols = st.columns([3, 1])
                with cols[0]:
                    if dish_match:
                        st.markdown(f"**{dish_match.group(1).strip()}**")
                    
                    if prep_match:
                        st.markdown(f"*{prep_match.group(1).strip()}*")
                    
                    if subst_match:
                        st.markdown(f"🔄 Alternative: {subst_match.group(1).strip()}")
                
                with cols[1]:
                    if calories_match:
                        st.markdown(f"**{calories_match.group(1).strip()}** calories")
                    
                    if macros_match:
                        st.caption(f"Carbs: {macros_match.group(1).strip()}")
                        st.caption(f"Protein: {macros_match.group(2).strip()}")
                        st.caption(f"Fat: {macros_match.group(3).strip()}")
                
                st.divider()
    
    # Render guidance sections
    if "General Guidance" in sections:
        with st.expander("Nutrition Guidelines"):
            guidance_text = "\n".join(sections["General Guidance"])
            bullet_points = [line.strip() for line in guidance_text.split('\n') if line.strip()]
            
            for point in bullet_points:
                if ':' in point:
                    title, desc = point.split(':', 1)
                    st.markdown(f"**{title.strip()}:** {desc.strip()}")
                else:
                    st.markdown(f"• {point}")
    
    return True  # Successfully rendered

# Initialize session state
if "user_id" not in st.session_state:
    st.session_state.user_id = f"user_{uuid.uuid4().hex[:8]}"
if "session_id" not in st.session_state:
    # We'll create this when user starts a new session
    st.session_state.session_id = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "user_profile_complete" not in st.session_state:
    st.session_state.user_profile_complete = False

# Function to create a new session
def create_session():
    try:
        # Generate a unique session ID
        session_id = f"session_{uuid.uuid4().hex[:8]}"
        
        # Create a new session via API
        response = requests.post(
            f"{API_BASE_URL}/apps/{APP_NAME}/users/{st.session_state.user_id}/sessions/{session_id}",
            json={"state": {}}
        )
        
        if response.status_code == 200:
            st.session_state.session_id = session_id
            st.session_state.messages = []
            return True
        else:
            st.error(f"Failed to create session: {response.text}")
            return False
    except Exception as e:
        st.error(f"Error creating session: {str(e)}")
        return False

# Function to send a message to the agent
def send_message(message):
    try:
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": message})
        
        # Prepare the API request
        payload = {
            "app_name": APP_NAME,
            "user_id": st.session_state.user_id,
            "session_id": st.session_state.session_id,
            "new_message": {
                "role": "user",
                "parts": [{"text": message}]
            }
        }
        
        # Make the API call
        with st.spinner("AI Coach is thinking..."):
            response = requests.post(
                f"{API_BASE_URL}/run",
                json=payload
            )
            
            if response.status_code == 200:
                events = response.json()
                
                # Process the response events
                for event in events:
                    if event.get("content", {}).get("role") == "model":
                        for part in event.get("content", {}).get("parts", []):
                            if "text" in part:
                                text = part["text"]
                                
                                # Check for structured data provided by our API middleware
                                structured_data = part.get("structured_data")
                                
                                # Add AI response to chat history with any structured data
                                if structured_data:
                                    st.session_state.messages.append({
                                        "role": "assistant",
                                        "content": text,
                                        "structured_data": structured_data
                                    })
                                else:
                                    st.session_state.messages.append({
                                        "role": "assistant",
                                        "content": text
                                    })
                
                # Force a rerun of the Streamlit app to update the UI immediately
                st.rerun()
            else:
                st.error(f"Error from API: {response.text}")
                
    except Exception as e:
        st.error(f"Error sending message: {str(e)}")

# Main UI layout with sidebar
st.sidebar.title("AI Fitness Coach 💪")

# Session Management in Sidebar
with st.sidebar.expander("Session Management", expanded=True):
    if st.session_state.session_id:
        st.write(f"Active Session: {st.session_state.session_id}")
        if st.button("Start New Session"):
            create_session()
    else:
        st.write("No active session")
        if st.button("Create Session"):
            create_session()

# User Profile Form in Sidebar
with st.sidebar.expander("Your Fitness Profile", expanded=not st.session_state.user_profile_complete):
    with st.form("user_profile_form"):
        st.write("Complete your profile to get personalized recommendations")
        name = st.text_input("Name")
        age = st.number_input("Age", min_value=16, max_value=100, value=30)
        gender = st.selectbox("Gender", ["Male", "Female", "Non-binary", "Prefer not to say"])
        weight = st.number_input("Weight (kg)", min_value=30.0, max_value=250.0, value=70.0, step=0.1)
        height = st.number_input("Height (cm)", min_value=100.0, max_value=250.0, value=170.0, step=0.1)
        
        fitness_level = st.select_slider(
            "Fitness Level",
            options=["Beginner", "Intermediate", "Advanced"]
        )
        
        goals = st.multiselect(
            "Fitness Goals",
            ["Weight loss", "Muscle gain", "Endurance", "Flexibility", "General health"]
        )
        
        dietary_restrictions = st.multiselect(
            "Dietary Restrictions (if any)",
            ["None", "Vegetarian", "Vegan", "Gluten-free", "Lactose-free", "Nut-free"]
        )
        
        submit_button = st.form_submit_button("Save Profile")
        
        if submit_button and name and goals:
            profile_info = (
                f"My name is {name}. I am {age} years old, {gender.lower()}. "
                f"I weigh {weight}kg and am {height}cm tall. "
                f"My fitness level is {fitness_level.lower()}. "
                f"My fitness goals are: {', '.join(goal.lower() for goal in goals)}. "
            )
            
            if dietary_restrictions and "None" not in dietary_restrictions:
                profile_info += f"I have the following dietary restrictions: {', '.join(dietary_restrictions)}. "
            
            # If we have an active session, send this profile info to the agent
            if st.session_state.session_id:
                send_message(f"Here's my profile information: {profile_info} Please help me achieve my fitness goals.")
                st.session_state.user_profile_complete = True
            else:
                st.warning("Please create a session before submitting your profile")

# Main chat area
st.title("Chat with your AI Fitness Coach")

# Display messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message["role"] == "assistant":
            # Check if this message has structured data
            if "structured_data" in message:
                structured_data = message["structured_data"]
                
                # Handle different types of structured data
                if structured_data.get("type") == "workout_plan":
                    # Render structured workout plan
                    st.subheader("📋 Your Personalized Workout Plan")
                    
                    # Render program structure in a highlighted box
                    with st.expander("Program Overview", expanded=True):
                        structure = structured_data.get("structure", {})
                        if structure:
                            for key, value in structure.items():
                                st.markdown(f"**{key.replace('_', ' ').title()}**: {value}")
                    
                    # Render workouts in tabs
                    workouts = structured_data.get("workouts", [])
                    if workouts:
                        tabs = st.tabs([f"{workout.get('name', f'Workout {i+1}')}" for i, workout in enumerate(workouts)])
                        
                        for i, workout in enumerate(workouts):
                            with tabs[i]:
                                # Show day info if available
                                if workout.get("day"):
                                    st.markdown(f"**{workout.get('day')}**")
                                
                                # Display exercises
                                exercises = workout.get("exercises", [])
                                for exercise in exercises:
                                    with st.container():
                                        cols = st.columns([3, 2])
                                        with cols[0]:
                                            st.markdown(f"**{exercise.get('name', '')}**")
                                            st.caption(f"{exercise.get('sets_reps', '')}")
                                        with cols[1]:
                                            st.markdown(f"💡 *{exercise.get('form_cue', '')}*")
                                        st.divider()
                    
                    # Render guidance sections in expandable sections
                    guidance = structured_data.get("guidance", {})
                    if guidance:
                        for section, content in guidance.items():
                            with st.expander(section.replace("_", " ").title()):
                                st.write(content)
                    
                    # Display regular text content as well
                    st.markdown("---")
                    st.write(message["content"])
                
                elif structured_data.get("type") == "meal_plan":
                    # Render structured meal plan
                    st.subheader("🍽️ Your Personalized Meal Plan")
                    
                    # Render summary in a highlighted box
                    summary = structured_data.get("summary", {})
                    if summary:
                        with st.expander("Plan Overview", expanded=True):
                            # Display calorie information
                            if "calories" in summary:
                                st.markdown(f"**Daily Calories:** {summary['calories']} kcal")
                            
                            # Display macronutrients
                            macros = summary.get("macros", {})
                            if macros:
                                st.markdown("**Macronutrients:**")
                                cols = st.columns(len(macros))
                                for i, (name, data) in enumerate(macros.items()):
                                    with cols[i]:
                                        st.metric(
                                            label=name.title(),
                                            value=f"{data.get('grams', 0)}g",
                                            delta=f"{data.get('percentage', 0)}%"
                                        )
                    
                    # Render meals
                    meals = structured_data.get("meals", [])
                    for meal in meals:
                        with st.container():
                            st.markdown(f"### {meal.get('name', 'Meal')}")
                            st.caption(f"Time: {meal.get('time', '')}")
                            
                            cols = st.columns([3, 1])
                            with cols[0]:
                                if meal.get("dish"):
                                    st.markdown(f"**{meal.get('dish')}**")
                                
                                if meal.get("preparation"):
                                    st.markdown(f"*{meal.get('preparation')}*")
                                
                                if meal.get("substitution"):
                                    st.markdown(f"🔄 Alternative: {meal.get('substitution')}")
                            
                            with cols[1]:
                                if meal.get("calories"):
                                    st.markdown(f"**{meal.get('calories')}** calories")
                                
                                macros = meal.get("macros", {})
                                if macros:
                                    for macro, value in macros.items():
                                        st.caption(f"{macro.title()}: {value}")
                            
                            st.divider()
                    
                    # Display guidance if available
                    if "guidance" in structured_data:
                        with st.expander("Nutrition Guidelines"):
                            guidance_text = structured_data["guidance"]
                            for line in guidance_text.split('\n'):
                                if line.strip():
                                    if ':' in line:
                                        title, desc = line.split(':', 1)
                                        st.markdown(f"**{title.strip()}:** {desc.strip()}")
                                    else:
                                        st.markdown(f"• {line.strip()}")
                    
                    # Display regular text content as well
                    st.markdown("---")
                    st.write(message["content"])
                
                else:
                    # If structured data type is unknown, fall back to text rendering
                    # Try to render as workout plan
                    if not render_workout_plan(message["content"]):
                        # If not a workout plan, try to render as meal plan
                        if not render_meal_plan(message["content"]):
                            # If not a structured plan, just display as regular text
                            st.write(message["content"])
            else:
                # Try to render as workout plan
                if not render_workout_plan(message["content"]):
                    # If not a workout plan, try to render as meal plan
                    if not render_meal_plan(message["content"]):
                        # If not a structured plan, just display as regular text
                        st.write(message["content"])
        else:
            # Regular user message
            st.write(message["content"])

# Chat input
if st.session_state.session_id:
    user_input = st.chat_input("Ask your fitness coach...")
    if user_input:
        send_message(user_input)
else:
    st.info("Please create a session using the sidebar to start chatting with your fitness coach!")

# Footer
st.markdown("---")
st.caption("AI Fitness Coach - Powered by Google ADK and Streamlit")

# Run the app with: streamlit run frontend.py 