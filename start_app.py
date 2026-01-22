#!/usr/bin/env python3
"""
Startup script for Pet Ingredient Safety Checker
Handles environment setup and runs the application
"""

import os
import sys
from pathlib import Path

def setup_environment():
    """Set up environment variables for development"""
    env_file = Path('.env')
    
    if not env_file.exists():
        print("⚠️  No .env file found. Creating one with default values...")
        
        # Create basic .env file for development
        env_content = """# Pet Ingredient Safety Checker - Environment Configuration

# OpenAI API Configuration (REQUIRED - Add your key here)
OPENAI_API_KEY=your_openai_api_key_here

# Database Configuration (SQLite for development)
DATABASE_URL=sqlite:///pet_safety.db

# Flask Configuration
FLASK_ENV=development
PORT=5000

# Security
SECRET_KEY=dev_secret_key_change_in_production
"""
        
        with open('.env', 'w') as f:
            f.write(env_content)
        
        print("✅ Created .env file. Please add your OpenAI API key!")
        print("   Edit .env and replace 'your_openai_api_key_here' with your actual API key.")
        return False
    
    return True

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import flask
        import flask_cors
        import sqlalchemy
        print("✅ Core dependencies found")
        return True
    except ImportError as e:
        print(f"❌ Missing dependencies: {e}")
        print("Please install dependencies:")
        print("  python -m venv venv")
        print("  source venv/bin/activate  # On Windows: venv\\Scripts\\activate")
        print("  pip install -r requirements.txt")
        return False

def start_application():
    """Start the application"""
    print("🐾 Starting Pet Ingredient Safety Checker...")
    print("=" * 50)
    
    # Check environment
    if not setup_environment():
        return
    
    # Check dependencies
    if not check_dependencies():
        return
    
    # Add backend to path
    backend_path = Path(__file__).parent / 'backend'
    sys.path.insert(0, str(backend_path))
    
    try:
        # Import and run the app
        from app import app
        
        print("🚀 Starting web server...")
        print("📱 Open your browser to: http://localhost:5000")
        print("🛑 Press Ctrl+C to stop the server")
        print("-" * 50)
        
        # Run the app
        app.run(host='0.0.0.0', port=5000, debug=True)
        
    except ImportError as e:
        print(f"❌ Error importing application: {e}")
        print("Make sure all dependencies are installed.")
    except Exception as e:
        print(f"❌ Error starting application: {e}")

if __name__ == '__main__':
    start_application()
