import pytest
import pandas as pd
from unittest.mock import patch

@pytest.fixture
def mock_who_data():
    """Fixture to provide mock WHO data."""
    return [
        {"indicator": "Life expectancy at birth (years)", "country": "USA", "year": 2020, "value": 77.0},
        {"indicator": "Life expectancy at birth (years)", "country": "USA", "year": 2021, "value": 76.0},
        {"indicator": "Life expectancy at birth (years)", "country": "CAN", "year": 2020, "value": 82.0},
        {"indicator": "Life expectancy at birth (years)", "country": "CAN", "year": 2021, "value": 81.0},
    ]

@pytest.fixture
def mock_world_bank_data():
    """Fixture to provide mock World Bank data."""
    return [
        {"indicator": "GDP per capita (current US$)", "country": "USA", "year": 2020, "value": 65000.0},
        {"indicator": "GDP per capita (current US$)", "country": "USA", "year": 2021, "value": 70000.0},
        {"indicator": "GDP per capita (current US$)", "country": "CAN", "year": 2020, "value": 50000.0},
        {"indicator": "GDP per capita (current US$)", "country": "CAN", "year": 2021, "value": 55000.0},
    ]

@pytest.fixture
def expected_processed_data():
    """Fixture to provide expected processed data."""
    return pd.DataFrame({
        'country': ['USA', 'USA', 'CAN', 'CAN'],
        'year': [2020, 2021, 2020, 2021],
        'life_expectancy': [77.0, 76.0, 82.0, 81.0],
        'gdp_per_capita': [65000.0, 70000.0, 50000.0, 55000.0]
    })

@pytest.fixture
def mock_api_response():
    """Fixture to mock API responses."""
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

        def json(self):
            return self.json_data

        def raise_for_status(self):
            if self.status_code >= 400:
                raise Exception("API Error")

    return MockResponse