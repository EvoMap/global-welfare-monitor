import pandas as pd
import json
from typing import List, Dict, Tuple
import numpy as np
import os

def parse_noaa_csv(csv_file_path: str) -> pd.DataFrame:
    """Parses NOAA climate data from a CSV file.

    Args:
        csv_file_path (str): The path to the NOAA CSV file.

    Returns:
        pd.DataFrame: A DataFrame containing the parsed data.

    Raises:
        FileNotFoundError: If the CSV file does not exist.
        pd.errors.EmptyDataError: If the CSV file is empty.
        pd.errors.ParserError: If there is an error parsing the CSV file.
    """
    try:
        df = pd.read_csv(csv_file_path)
        return df
    except FileNotFoundError:
        raise FileNotFoundError(f"NOAA CSV file not found at: {csv_file_path}")
    except pd.errors.EmptyDataError:
        raise pd.errors.EmptyDataError(f"NOAA CSV file is empty: {csv_file_path}")
    except pd.errors.ParserError:
        raise pd.errors.ParserError(f"Error parsing NOAA CSV file: {csv_file_path}")
    except Exception as e:
        raise Exception(f"An unexpected error occurred while parsing NOAA CSV: {e}")


def calculate_regional_temperature_anomalies(df: pd.DataFrame, region_col: str, temp_col: str, base_period_start: int, base_period_end: int) -> pd.DataFrame:
    """Calculates regional temperature anomalies based on a base period.

    Args:
        df (pd.DataFrame): DataFrame containing temperature data with a region column and a temperature column.
        region_col (str): Name of the column containing region information.
        temp_col (str): Name of the column containing temperature data.
        base_period_start (int): Start year of the base period.
        base_period_end (int): End year of the base period.

    Returns:
        pd.DataFrame: DataFrame with added 'temperature_anomaly' column.
    """
    try:
        # Validate input DataFrame
        if df.empty:
            raise ValueError("Input DataFrame is empty.")
        if region_col not in df.columns or temp_col not in df.columns:
            raise ValueError(f"Region column '{region_col}' or temperature column '{temp_col}' not found in DataFrame.")

        # Calculate the mean temperature for each region during the base period
        base_period_data = df[(df['year'] >= base_period_start) & (df['year'] <= base_period_end)]
        regional_base_temps = base_period_data.groupby(region_col)[temp_col].mean().reset_index()
        regional_base_temps.rename(columns={temp_col: 'base_temperature'}, inplace=True)

        # Merge the base temperatures back into the original DataFrame
        df = pd.merge(df, regional_base_temps, on=region_col, how='left')

        # Calculate the temperature anomaly for each region and year
        df['temperature_anomaly'] = df[temp_col] - df['base_temperature']

        df.drop(columns=['base_temperature'], inplace=True)

        return df

    except ValueError as ve:
        print(f"ValueError: {ve}")
        return pd.DataFrame()  # Return an empty DataFrame in case of error
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return pd.DataFrame()  # Return an empty DataFrame in case of error


def compute_sea_level_trend_analysis(df: pd.DataFrame, year_col: str, sea_level_col: str) -> Dict[str, float]:
    """Computes sea level trend analysis using linear regression.

    Args:
        df (pd.DataFrame): DataFrame containing sea level data with year and sea level columns.
        year_col (str): Name of the column containing year data.
        sea_level_col (str): Name of the column containing sea level data.

    Returns:
        Dict[str, float]: A dictionary containing the slope (trend) and intercept of the linear regression.
    """
    try:
        # Validate input DataFrame
        if df.empty:
            raise ValueError("Input DataFrame is empty.")
        if year_col not in df.columns or sea_level_col not in df.columns:
            raise ValueError(f"Year column '{year_col}' or sea level column '{sea_level_col}' not found in DataFrame.")

        # Perform linear regression
        x = df[year_col]
        y = df[sea_level_col]
        slope, intercept = np.polyfit(x, y, 1)

        return {"slope": slope, "intercept": intercept}

    except ValueError as ve:
        print(f"ValueError: {ve}")
        return {"slope": np.nan, "intercept": np.nan}  # Return NaN values in case of error
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return {"slope": np.nan, "intercept": np.nan}  # Return NaN values in case of error


def generate_json_summary_report(regional_anomalies: pd.DataFrame, sea_level_trend: Dict[str, float], report_path: str) -> None:
    """Generates a structured JSON summary report.

    Args:
        regional_anomalies (pd.DataFrame): DataFrame containing regional temperature anomalies.
        sea_level_trend (Dict[str, float]): Dictionary containing sea level trend analysis results.
        report_path (str): The path to save the JSON report.

    Returns:
        None
    """
    try:
        # Convert regional anomalies DataFrame to a list of dictionaries
        regional_anomalies_list = regional_anomalies.to_dict(orient='records')

        # Create the summary report
        summary_report = {
            "regional_temperature_anomalies": regional_anomalies_list,
            "sea_level_trend_analysis": sea_level_trend
        }

        # Save the summary report to a JSON file
        output_dir = os.path.dirname(report_path)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        with open(report_path, 'w') as f:
            json.dump(summary_report, f, indent=4)

        print(f"JSON summary report generated and saved to: {report_path}")

    except Exception as e:
        print(f"An unexpected error occurred while generating the JSON report: {e}")


if __name__ == '__main__':
    # Example Usage (replace with actual file paths and data)
    noaa_data_path = 'data/noaa_data.csv'  # Replace with your actual data path
    report_output_path = 'reports/climate_summary.json'  # Replace with your desired output path

    # Create dummy data for demonstration
    data = {
        'year': [2010, 2011, 2012, 2010, 2011, 2012],
        'region': ['North', 'North', 'North', 'South', 'South', 'South'],
        'temperature': [10, 11, 12, 20, 21, 22],
        'sea_level': [5, 6, 7, 8, 9, 10]
    }
    df = pd.DataFrame(data)
    df.to_csv(noaa_data_path, index=False)

    # Parse NOAA data
    try:
        noaa_df = parse_noaa_csv(noaa_data_path)
    except Exception as e:
        print(f"Error parsing NOAA data: {e}")
        noaa_df = pd.DataFrame()

    if not noaa_df.empty:
        # Calculate regional temperature anomalies
        regional_anomalies_df = calculate_regional_temperature_anomalies(noaa_df, 'region', 'temperature', 2010, 2011)

        # Compute sea level trend analysis
        sea_level_trend_results = compute_sea_level_trend_analysis(noaa_df, 'year', 'sea_level')

        # Generate JSON summary report
        generate_json_summary_report(regional_anomalies_df, sea_level_trend_results, report_output_path)
