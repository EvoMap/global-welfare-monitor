"""FastAPI application for the Global Welfare Monitor."""

from fastapi import FastAPI
from fastapi.responses import JSONResponse
import os

app = FastAPI()

DATA_DIR = os.environ.get("DATA_DIR", "/data")

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return JSONResponse({"status": "ok"})

@app.get("/data")
async def get_data():
    """Example endpoint to serve data."""
    # Replace with actual data loading logic from DATA_DIR
    data = {"message": f"Data from {DATA_DIR}"}
    return JSONResponse(data)
