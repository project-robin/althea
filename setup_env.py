"""
Script to create the .env file for the fitness_coach application.
Run this script to set up the environment variables for the Google API key.
"""

import os

def create_env_file():
    # Create the path to the .env file
    env_file_path = os.path.join('fitness_coach', '.env')
    
    # Get API key from user
    api_key = input("Enter your Google API key: ")
    
    # Create the content for the .env file
    env_content = f"""# Google AI API configuration
GOOGLE_API_KEY={api_key}

# Or for Google Cloud (Vertex AI)
# VERTEXAI=true
# PROJECT=your_gcp_project_id
# LOCATION=us-central1
"""
    
    # Write the content to the .env file
    with open(env_file_path, 'w') as f:
        f.write(env_content)
    
    print(f".env file created successfully at {env_file_path}")
    print("You can now run 'conda activate chatgpt && adk web' to start the server.")

if __name__ == "__main__":
    create_env_file() 