#!/usr/bin/env python3
"""
Pet Ingredient Safety Checker - Production Server Entry Point
Uses Gunicorn for production deployments
"""

import os
import sys

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the Flask app
from app import app

# Configure for production
app.config['PROPAGATE_EXCEPTIONS'] = True

if __name__ == '__main__':
    # This is used for local development only
    # In production, use: gunicorn --bind 0.0.0.0:$PORT simple_server:app
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
