"""
Setup script for the Fitness Coach application.
This script helps users install dependencies and configure their environment.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_python_version():
    """Check if Python version is 3.10 or higher"""
    required_version = (3, 10)
    current_version = sys.version_info[:2]
    
    if current_version < required_version:
        print(f"Error: Python {required_version[0]}.{required_version[1]} or higher is required.")
        print(f"Current Python version: {current_version[0]}.{current_version[1]}")
        sys.exit(1)
        
    print(f"✅ Python version {current_version[0]}.{current_version[1]} is compatible")

def setup_virtual_env():
    """Set up a virtual environment if it doesn't exist"""
    venv_path = Path(".venv")
    
    if not venv_path.exists():
        print("Creating virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", ".venv"], check=True)
        print("✅ Virtual environment created")
    else:
        print("✅ Virtual environment already exists")
        
    # Determine the correct activation script
    if os.name == "nt":  # Windows
        activate_script = venv_path / "Scripts" / "activate"
    else:  # Unix/Linux/MacOS
        activate_script = venv_path / "bin" / "activate"
        
    print(f"\nTo activate the virtual environment, run:")
    if os.name == "nt":  # Windows
        print(f"    .venv\\Scripts\\activate")
    else:
        print(f"    source .venv/bin/activate")

def install_dependencies():
    """Install dependencies from requirements.txt"""
    print("\nInstalling dependencies...")
    
    pip_cmd = [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"]
    result = subprocess.run(pip_cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ Dependencies installed successfully")
    else:
        print("❌ Error installing dependencies:")
        print(result.stderr)
        sys.exit(1)

def create_env_file():
    """Create .env file if it doesn't exist"""
    env_path = Path(".env")
    env_example_path = Path("env.example")
    
    if not env_path.exists():
        if env_example_path.exists():
            shutil.copy(env_example_path, env_path)
            print("\n✅ Created .env file from env.example")
            print("⚠️  Please edit the .env file to set your API keys")
        else:
            with open(env_path, "w") as f:
                f.write("# Google API key for ADK\n")
                f.write("GOOGLE_GENAI_USE_VERTEXAI=FALSE\n")
                f.write("GOOGLE_API_KEY=your_api_key_here\n\n")
                f.write("# Frontend configuration\n")
                f.write("API_BASE_URL=http://localhost:8000\n")
            print("\n✅ Created default .env file")
            print("⚠️  Please edit the .env file to set your API keys")
    else:
        print("\n✅ .env file already exists")

def print_next_steps():
    """Print instructions for next steps"""
    print("\n" + "="*60)
    print("SETUP COMPLETE!")
    print("="*60)
    print("\nNext steps:")
    print("1. Activate the virtual environment")
    if os.name == "nt":  # Windows
        print("   .venv\\Scripts\\activate")
    else:
        print("   source .venv/bin/activate")
    print("\n2. Edit the .env file with your API keys")
    print("\n3. Start the backend:")
    print("   python api.py")
    print("\n4. In a new terminal, start the frontend:")
    print("   streamlit run frontend.py")
    print("\n" + "="*60)

def main():
    """Main setup function"""
    print("Setting up Fitness Coach application...\n")
    
    check_python_version()
    setup_virtual_env()
    install_dependencies()
    create_env_file()
    print_next_steps()

if __name__ == "__main__":
    main() 