#!/usr/bin/env python
"""
Wrapper script to run uvicorn with proper Python path setup.
Ensures imports like 'from backend.config' work in Docker containers.
"""

import sys
from pathlib import Path

# Ensure the backend directory is in Python path for imports
# This must be done BEFORE any imports from backend modules
app_dir = Path(__file__).parent
sys.path.insert(0, str(app_dir))

# Now we can import our application
from main import app

# Run uvicorn directly with the app instance
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=False
    )
