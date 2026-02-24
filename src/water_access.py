""
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from typing import Optional, Tuple, List, Dict, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def parse_wash_data(data: List[Dict[str, Any]]) -> pd.DataFrame:
    """Parses WASH (Water, Sanitation, Hygiene) indicator data.

    Args:
        data (list): A list of dictionaries, where each dictionary represents
                     a WASH indicator record.

    Returns:
        pd.DataFrame: A DataFrame containing the parsed WASH data.
                      Returns an empty DataFrame if input data is invalid.
    """
    try:
        if not isinstance(data, list) or not data:
            logging.warning("Input WASH data is empty or not a list.")
            return pd.DataFrame()

        df = pd.DataFrame(data)
        if not {'country', 'year', 'indicator', 'value'}.issubset(df.columns):
            logging.error(
                "Required columns ('country', 'year', 'indicator', 'value') are missing."
            )
            return pd.DataFrame()

        df['year'] = pd.to_numeric(df['year'], errors='coerce')
        df = df.dropna(subset=['year'])
        df['year'] = df['year'].astype(int)
        df['value'] = pd.to_numeric(df['value'], errors='coerce')
        df = df.dropna(subset=['value'])
        return df
    except (ValueError, TypeError) as e:
        logging.error(f"Error parsing WASH data: {e}")
        return pd.DataFrame()


def calculate_safe_water_coverage(data: pd.DataFrame, region: str) -> Optional[float]:
    """Calculates safe drinking water coverage for a given region.

    Args:
        data (pd.DataFrame): A DataFrame containing WASH data.
        region (str): The region for which to calculate coverage.

    Returns:
        Optional[float]: The safe drinking water coverage percentage for the region,
                         or None if data is insufficient or invalid.
    """
    try:
        region_data = data[data['country'] == region]
        if region_data.empty:
            logging.warning(f"No data found for region: {region}")
            return None

        water_access_data = region_data[
            region_data['indicator'].str.contains('Improved water source', na=False)
        ]

        if water_access_data.empty:
            logging.warning(f"No safe water access data found for region: {region}")
            return None

        coverage = water_access_data['value'].mean()
        if not isinstance(coverage, (int, float)):
            logging.warning(f"Invalid coverage value for region: {region}")
            return None

        return float(coverage)

    except Exception as e:
        logging.error(f"Error calculating safe water coverage: {e}")
        return None


def aggregate_water_quality_index(data: pd.DataFrame, region: str) -> Optional[float]:
    """Aggregates water quality index for a given region.

    Args:
        data (pd.DataFrame): A DataFrame containing water quality data.
        region (str): The region for which to aggregate the index.

    Returns:
        Optional[float]: The aggregated water quality index for the region,
                         or None if data is insufficient.
    """
    try:
        region_data = data[data['country'] == region]
        if region_data.empty:
            logging.warning(f"No data found for region: {region}")
            return None

        quality_data = region_data[region_data['indicator'].str.contains('Water quality index', na=False)]

        if quality_data.empty:
            logging.warning(f"No water quality index data found for region: {region}")
            return None

        index = quality_data['value'].mean()
        if not isinstance(index, (int, float)):
            logging.warning(f"Invalid water quality index value for region: {region}")
            return None

        return float(index)

    except Exception as e:
        logging.error(f"Error aggregating water quality index: {e}")
        return None


def project_trend(data: pd.DataFrame, region: str, indicator: str, years: int = 5) -> Optional[float]:
    """Projects the trend of a specific indicator for a given region using linear regression.

    Args:
        data (pd.DataFrame): A DataFrame containing WASH data.
        region (str): The region for which to project the trend.
        indicator (str): The indicator for which to project the trend.
        years (int): The number of years into the future to project.

    Returns:
        Optional[float]: The projected value of the indicator after the specified number of years,
                         or None if the projection fails.
    """
    try:
        region_data = data[(data['country'] == region) & (data['indicator'] == indicator)].copy()
        if region_data.empty:
            logging.warning(f"No data found for region: {region} and indicator: {indicator}")
            return None

        # Sort data by year
        region_data = region_data.sort_values('year')

        # Prepare data for linear regression
        X = region_data['year'].values.reshape(-1, 1)
        y = region_data['value'].values

        # Check if there's enough data for regression
        if len(X) < 2:
            logging.warning(
                f"Insufficient data points for linear regression for region: {region} and indicator: {indicator}"
            )
            return None

        # Train the linear regression model
        model = LinearRegression()
        model.fit(X, y)

        # Project the trend
        future_year = X[-1, 0] + years
        projected_value = model.predict([[future_year]])[0]

        return float(projected_value)

    except Exception as e:
        logging.error(f"Error projecting trend: {e}")
        return None
""