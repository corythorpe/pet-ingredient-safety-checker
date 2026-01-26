#!/usr/bin/env python3
"""
Pet Ingredient Safety Checker - Simple Server Entry Point
This file serves as the entry point for DigitalOcean App Platform deployment
"""

import os
import sys

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import and run the main application
from app import app

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
