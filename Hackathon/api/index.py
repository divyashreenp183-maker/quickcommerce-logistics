"""
Vercel serverless entry point for Quick Commerce Logistics System
"""

import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app

# Vercel expects a handler function
handler = app

# For local testing
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
