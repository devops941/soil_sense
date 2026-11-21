"""
SoilSense - Backend Runner Script
Starts FastAPI backend server on http://127.0.0.1:8001
"""

import sys
import os
from pathlib import Path

# Add backend directory to sys.path and ensure current working dir is backend
backend_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_dir))
os.chdir(str(backend_dir))

import uvicorn

if __name__ == "__main__":
    print("🌱 Starting SoilSense Backend on http://127.0.0.1:8001 ...")
    uvicorn.run("app.main:app", host="127.0.0.1", port=8001, reload=True)
