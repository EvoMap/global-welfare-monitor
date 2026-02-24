"""FastAPI application for the Global Welfare Monitor project.

This module defines the API endpoints for accessing welfare data, including
health indicators, disaster alerts, and weekly reports.
"""

import os
from datetime import date
from typing import Optional, List, Dict, Any

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Global Welfare Monitor API")

# CORS configuration
origins = [
    "*",  # Allows all origins (for development purposes)
    # Add specific origins in production, e.g., "https://example.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Mock data (replace with actual data access logic)
INDICATORS = {
    "life_expectancy": {
        "description": "Average life expectancy at birth",
        "data": [
            {"country": "USA", "date": "2023-01-01", "value": 77.0},
            {"country": "USA", "date": "2023-01-08", "value": 77.1},
            {"country": "Canada", "date": "2023-01-01", "value": 82.0},
        ],
    },
    "food_prices": {
        "description": "Average price of staple foods",
        "data": [
            {"country": "Kenya", "date": "2023-01-01", "value": 1.2},
            {"country": "Kenya", "date": "2023-01-08", "value": 1.3},
            {"country": "Ethiopia", "date": "2023-01-01", "value": 1.0},
        ],
    },
}

ALERTS = [
    {"country": "Turkey", "date": "2023-02-06", "type": "Earthquake", "severity": "High"},
    {"country": "Syria", "date": "2023-02-06", "type": "Earthquake", "severity": "High"},
]

REPORTS = {
    "latest": {
        "date": "2024-01-29",
        "summary": "Global welfare indicators show a slight improvement in food security but a decline in mental health.",
        "details_url": "https://example.com/reports/2024-01-29"
    }
}


@app.get("/health", tags=["Health Check"])
async def health_check():
    """Check the health of the API."""
    return {"status": "ok"}


@app.get("/indicators", tags=["Indicators"])
async def list_indicators():
    """List all available welfare indicators."""
    return list(INDICATORS.keys())


@app.get("/indicators/{name}", tags=["Indicators"])
async def get_indicator(name: str, country: Optional[str] = None, date: Optional[date] = None):
    """Get data for a specific indicator, with optional filtering.

    Args:
        name: The name of the indicator.
        country: Optional country filter.
        date: Optional date filter.

    Returns:
        The indicator data, filtered by country and date if provided.

    Raises:
        HTTPException: If the indicator is not found.
    """
    if name not in INDICATORS:
        raise HTTPException(status_code=404, detail="Indicator not found")

    data = INDICATORS[name]["data"]

    # Apply filters
    filtered_data = data
    if country:
        filtered_data = [item for item in filtered_data if item["country"] == country]
    if date:
        filtered_data = [item for item in filtered_data if item["date"] == str(date)]

    return filtered_data


@app.get("/alerts", tags=["Alerts"])
async def get_alerts():
    """Get recent disaster alerts."""
    return ALERTS


@app.get("/report/latest", tags=["Reports"])
async def get_latest_report():
    """Get the latest weekly report summary."""
    return REPORTS["latest"]


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
