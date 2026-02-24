import pandas as pd
import pytest
from src import report_generator
import json
import os


def test_generate_markdown_report():
    data = pd.DataFrame({
        'col1': [1, 2, 3],
        'col2': ['a', 'b', 'c']
    })
    title = "Test Report"
    description = "This is a test report."
    report = report_generator.generate_markdown_report(data, title, description)
    assert isinstance(report, str)
    assert "Test Report" in report
    assert "This is a test report." in report
    assert "col1" in report
    assert "col2" in report


def test_export_to_csv(tmp_path):
    data = pd.DataFrame({
        'col1': [1, 2, 3],
        'col2': ['a', 'b', 'c']
    })
    filepath = str(tmp_path / "test.csv")
    result = report_generator.export_to_csv(data, filepath)
    assert result is True
    with open(filepath, 'r') as f:
        content = f.read()
        assert "col1,col2" in content
        assert "1,a" in content


def test_format_as_json_api_response():
    data = {"key": "value"}
    response = report_generator.format_as_json_api_response(data)
    assert isinstance(response, dict)
    assert response["status_code"] == 200
    assert response["message"] == "Success"
    assert response["data"] == data


@pytest.fixture
def sample_dataframe():
    """Fixture to provide a sample Pandas DataFrame."""
    data = {
        'country': ['USA', 'Canada', 'Mexico'],
        'year': [2020, 2020, 2020],
        'life_expectancy': [77, 82, 75],
        'gdp_per_capita': [65000, 50000, 10000]
    }
    return pd.DataFrame(data)


def test_generate_historical_comparison_report(tmp_path, sample_dataframe):
    """Test generating a historical comparison report."""
    data1 = pd.DataFrame({
        'country': ['USA', 'Canada'],
        'year': [2020, 2020],
        'life_expectancy': [77, 82]
    })

    data2 = pd.DataFrame({
        'country': ['USA', 'Canada'],
        'year': [2021, 2021],
        'life_expectancy': [78, 83]
    })

    output_path = str(tmp_path / "historical_comparison.csv")
    report_generator.generate_historical_comparison_report(
        data1,
        '2020',
        data2,
        '2021',
        ['country'],
        output_path
    )

    assert os.path.exists(output_path)
    comparison_df = pd.read_csv(output_path)
    assert 'year_2020' in comparison_df.columns
    assert 'year_2021' in comparison_df.columns
    assert 'life_expectancy_2020' in comparison_df.columns
    assert 'life_expectancy_2021' in comparison_df.columns
    assert len(comparison_df) == 2
