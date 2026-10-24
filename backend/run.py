#!/usr/bin/env python
"""
Wrapper script to run uvicorn with proper Python path setup.
Ensures imports like 'from backend.config' work in Docker containers.
"""

import sys
from pathlib import Path

# Ensure the backend directory is in Python path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Now run uvicorn
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False
    )
