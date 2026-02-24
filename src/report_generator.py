"""Module for generating reports and exporting data from the Global Welfare Monitor.

This module provides functionalities for generating markdown reports with tables and statistics,
CSV export of processed metrics, JSON API response formatting, and historical comparison report generation.
"""

import csv
import json
import logging
import os
from typing import Any, Dict, List, Optional

import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def generate_markdown_report(data: pd.DataFrame, title: str, description: str) -> str:
    """Generates a markdown report with tables and statistics from a Pandas DataFrame.

    Args:
        data (pd.DataFrame): The data to include in the report.
        title (str): The title of the report.
        description (str): A brief description of the report.

    Returns:
        str: A markdown formatted string representing the report.
    """
    try:
        report = f"# {title}\n\n{description}\n\n"

        # Add summary statistics
        report += "## Summary Statistics\n\n"
        report += data.describe().to_markdown() + "\n\n"

        # Add data table
        report += "## Data Table\n\n"
        report += data.to_markdown(index=False) + "\n"

        return report
    except Exception as e:
        logging.error(f"Error generating markdown report: {e}")
        return f"Error generating report: {e}"


def export_to_csv(data: pd.DataFrame, filepath: str) -> bool:
    """Exports a Pandas DataFrame to a CSV file.

    Args:
        data (pd.DataFrame): The data to export.
        filepath (str): The path to save the CSV file.

    Returns:
        bool: True if the export was successful, False otherwise.
    """
    try:
        data.to_csv(filepath, index=False)
        logging.info(f"Data successfully exported to CSV: {filepath}")
        return True
    except Exception as e:
        logging.error(f"Error exporting to CSV: {e}")
        return False


def format_as_json_api_response(data: Any, status_code: int = 200, message: str = "Success") -> Dict[str, Any]:
    """Formats data into a standard JSON API response.

    Args:
        data (Any): The data to include in the response.
        status_code (int): The HTTP status code.
        message (str): A message describing the response.

    Returns:
        Dict[str, Any]: A dictionary representing the JSON API response.
    """
    response = {
        "status_code": status_code,
        "message": message,
        "data": data
    }
    return response


def generate_historical_comparison_report(
    data1: pd.DataFrame,
    data1_name: str,
    data2: pd.DataFrame,
    data2_name: str,
    common_columns: List[str],
    output_path: str,
) -> None:
    """Generates a historical comparison report and saves it to a file.

    Args:
        data1 (pd.DataFrame): First dataframe for comparison.
        data1_name (str): Name or description for the first dataset.
        data2 (pd.DataFrame): Second dataframe for comparison.
        data2_name (str): Name or description for the second dataset.
        common_columns (List[str]): Columns to compare between the two dataframes.
        output_path (str): Path to save the comparison report (CSV).

    Returns:
        None
    """
    try:
        # Merge the two dataframes on common columns
        merged_data = pd.merge(
            data1,
            data2,
            on=common_columns,
            suffixes=('_' + data1_name, '_' + data2_name),
            how='outer',
        )

        # Save the merged data to a CSV file
        merged_data.to_csv(output_path, index=False)
        logging.info(f"Historical comparison report saved to {output_path}")
    except Exception as e:
        logging.error(f"Error generating historical comparison report: {e}")


if __name__ == '__main__':
    # Example Usage
    data = pd.DataFrame({
        'country': ['USA', 'Canada', 'Mexico'],
        'year': [2020, 2020, 2020],
        'life_expectancy': [77, 82, 75],
        'gdp_per_capita': [65000, 50000, 10000]
    })

    # Generate a markdown report
    markdown_report = generate_markdown_report(
        data, "Sample Report", "This is a sample report."
    )
    print(markdown_report)

    # Export to CSV
    export_to_csv(data, "sample_data.csv")

    # Format as JSON API response
    json_response = format_as_json_api_response(
        data.to_dict(orient='records'), status_code=200, message="Success"
    )
    print(json.dumps(json_response, indent=4))

    # Generate a historical comparison report
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

    generate_historical_comparison_report(
        data1,
        '2020',
        data2,
        '2021',
        ['country'],
        'historical_comparison.csv',
    )
