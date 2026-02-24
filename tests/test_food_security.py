import pytest
import pandas as pd
from src.food_security import FoodSecurityMonitor
import logging

# Mock data for testing
mock_ipc_data = pd.DataFrame({
    'region': ['A', 'B', 'C'],
    'phase': [3, 4, 5]
})

mock_population_data = pd.DataFrame({
    'region': ['A', 'B', 'C'],
    'population': [1000, 2000, 3000],
    'average_calories_consumed': [1800, 1500, 1200]
})

mock_price_data = pd.DataFrame({
    'date': pd.to_datetime(['2023-01-01', '2023-01-08', '2023-01-15',
                               '2023-01-01', '2023-01-08', '2023-01-15']),
    'region': ['A', 'A', 'A', 'B', 'B', 'B'],
    'price': [1.0, 1.1, 1.2, 1.5, 1.6, 1.7]
})


@pytest.fixture
def food_security_monitor():
    alert_thresholds = {
        "caloric_deficit": {"high": 10, "critical": 20},
        "price_volatility": {"high": 0.3, "critical": 0.5}
    }
    return FoodSecurityMonitor(alert_thresholds)


def test_parse_ipc_data(food_security_monitor, tmp_path):
    # Create a temporary CSV file for testing
    csv_path = tmp_path / 'mock_ipc_data.csv'
    mock_ipc_data.to_csv(csv_path, index=False)

    df = food_security_monitor.parse_ipc_data(str(csv_path))
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert 'region' in df.columns
    assert 'phase' in df.columns


def test_parse_ipc_data_file_not_found(food_security_monitor):
    with pytest.raises(FileNotFoundError):
        food_security_monitor.parse_ipc_data('non_existent_file.csv')


def test_parse_ipc_data_empty_file(food_security_monitor, tmp_path):
    # Create an empty temporary CSV file
    csv_path = tmp_path / 'empty_ipc_data.csv'
    pd.DataFrame().to_csv(csv_path, index=False)

    with pytest.raises(pd.errors.EmptyDataError):
        food_security_monitor.parse_ipc_data(str(csv_path))


def test_calculate_caloric_deficit(food_security_monitor):
    caloric_deficit_data = food_security_monitor.calculate_caloric_deficit(mock_population_data.copy())
    assert isinstance(caloric_deficit_data, pd.DataFrame)
    assert 'region' in caloric_deficit_data.columns
    assert 'caloric_deficit_percentage' in caloric_deficit_data.columns
    # Example calculation check
    assert caloric_deficit_data['caloric_deficit'][0] == 300
    assert caloric_deficit_data['caloric_deficit_percentage'][0] == (300/2100)*100


def test_calculate_caloric_deficit_invalid_data(food_security_monitor):
    invalid_population_data = mock_population_data.drop(columns=['population'])
    with pytest.raises(ValueError):
        food_security_monitor.calculate_caloric_deficit(invalid_population_data)


def test_calculate_food_price_volatility(food_security_monitor):
    price_volatility_data = food_security_monitor.calculate_food_price_volatility(mock_price_data.copy())
    assert isinstance(price_volatility_data, pd.DataFrame)
    assert 'region' in price_volatility_data.columns
    assert 'price_volatility' in price_volatility_data.columns


def test_calculate_food_price_volatility_invalid_data(food_security_monitor):
    invalid_price_data = mock_price_data.drop(columns=['price'])
    with pytest.raises(ValueError):
        food_security_monitor.calculate_food_price_volatility(invalid_price_data)


def test_assess_alerts(food_security_monitor):
    # Create mock dataframes for caloric deficit and price volatility
    mock_caloric_deficit_data = pd.DataFrame({
        'region': ['A', 'B', 'C'],
        'caloric_deficit_percentage': [5, 15, 25]
    })
    mock_price_volatility_data = pd.DataFrame({
        'region': ['A', 'B', 'C'],
        'price_volatility': [0.2, 0.4, 0.6]
    })

    alerts = food_security_monitor.assess_alerts(mock_caloric_deficit_data, mock_price_volatility_data)

    assert isinstance(alerts, dict)
    assert 'high' in alerts
    assert 'critical' in alerts
    assert 'B' in alerts['high']  # Caloric deficit for region B is 15, which is >= high threshold (10)
    assert 'C' in alerts['critical']  # Caloric deficit for region C is 25, which is >= critical threshold (20)
    assert 'B' in alerts['critical'] # Price volatility for region B is 0.4, which is >= high threshold (0.3)
    assert 'C' in alerts['critical'] # Price volatility for region C is 0.6, which is >= critical threshold (0.5)
