import pytest
import pandas as pd
from src import climate_dashboard
import json
import os

# Mock data for testing
mock_noaa_data = pd.DataFrame({
    'year': [2010, 2011, 2012, 2010, 2011, 2012],
    'region': ['North', 'North', 'North', 'South', 'South', 'South'],
    'temperature': [10, 11, 12, 20, 21, 22],
    'sea_level': [5, 6, 7, 8, 9, 10]
})


@pytest.fixture
def mock_noaa_csv(tmp_path):
    # Create a temporary CSV file for testing
    csv_path = tmp_path / 'mock_noaa_data.csv'
    mock_noaa_data.to_csv(csv_path, index=False)
    return str(csv_path)


def test_parse_noaa_csv(mock_noaa_csv):
    """Test parsing NOAA CSV file.
    """
    df = climate_dashboard.parse_noaa_csv(mock_noaa_csv)
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert 'year' in df.columns
    assert 'region' in df.columns
    assert 'temperature' in df.columns


def test_parse_noaa_csv_file_not_found():
    """Test parsing NOAA CSV when file not found.
    """
    with pytest.raises(FileNotFoundError):
        climate_dashboard.parse_noaa_csv('non_existent_file.csv')


def test_calculate_regional_temperature_anomalies():
    """Test calculating regional temperature anomalies.
    """
    df = mock_noaa_data.copy()
    anomalies_df = climate_dashboard.calculate_regional_temperature_anomalies(df, 'region', 'temperature', 2010, 2011)
    assert 'temperature_anomaly' in anomalies_df.columns
    # Example: Check anomaly for North in 2012. Base temp is (10+11)/2 = 10.5. Anomaly = 12 - 10.5 = 1.5
    north_2012_anomaly = anomalies_df[(anomalies_df['region'] == 'North') & (anomalies_df['year'] == 2012)]['temperature_anomaly'].values[0]
    assert abs(north_2012_anomaly - 1.5) < 0.001 # Using abs and a small tolerance for floating point comparison


def test_compute_sea_level_trend_analysis():
    """Test computing sea level trend analysis.
    """
    df = mock_noaa_data.copy()
    trend_analysis = climate_dashboard.compute_sea_level_trend_analysis(df, 'year', 'sea_level')
    assert 'slope' in trend_analysis
    assert 'intercept' in trend_analysis
    assert abs(trend_analysis['slope'] - 1.0) < 0.001 # Expected slope is 1.0
    assert abs(trend_analysis['intercept'] - (-15.0)) < 0.001 # Expected intercept is -15.0


@pytest.fixture
def mock_report_path(tmp_path):
    # Create a temporary file path for the report
    report_path = tmp_path / 'climate_summary.json'
    return str(report_path)


def test_generate_json_summary_report(mock_report_path):
    """Test generating JSON summary report.
    """
    regional_anomalies = pd.DataFrame({
        'year': [2012],
        'region': ['North'],
        'temperature_anomaly': [1.5]
    })
    sea_level_trend = {
        'slope': 1.0,
        'intercept': -15.0
    }

    climate_dashboard.generate_json_summary_report(regional_anomalies, sea_level_trend, mock_report_path)

    # Verify that the report file was created
    assert os.path.exists(mock_report_path)

    # Verify the contents of the report
    with open(mock_report_path, 'r') as f:
        report_data = json.load(f)

    assert 'regional_temperature_anomalies' in report_data
    assert 'sea_level_trend_analysis' in report_data
    assert len(report_data['regional_temperature_anomalies']) == 1
    assert report_data['sea_level_trend_analysis']['slope'] == 1.0
