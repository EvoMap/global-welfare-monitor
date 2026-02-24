#!/bin/bash

# Activate the virtual environment
. venv/bin/activate

# Run the FastAPI application using Uvicorn
uvicorn src.main:app --host 0.0.0.0 --port 8000