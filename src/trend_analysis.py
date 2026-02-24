"""
This script performs trend analysis on welfare data, calculating moving averages
and identifying trends in key indicators over time. The results are saved to
data/analysis/trend_analysis.csv.
"""

import pandas as pd
import numpy as np
import os

DATA_DIR = 'data'
ANALYSIS_DIR = os.path.join(DATA_DIR, 'analysis')
TREND_ANALYSIS_FILE = os.path.join(ANALYSIS_DIR, 'trend_analysis.csv')

def calculate_moving_average(data, window=5):
    """Calculates the moving average of a given time series.

    Args:
        data (pd.Series): The time series data.
        window (int): The window size for the moving average.

    Returns:
        pd.Series: The moving average of the data.
    """
    return data.rolling(window=window).mean()


def identify_trend(data):
    """Identifies the trend in a given time series.

    Args:
        data (pd.Series): The time series data.

    Returns:
        str: 'Increasing', 'Decreasing', or 'Stable'.
    """
    if len(data) < 2:
        return 'Stable'

    slope = np.polyfit(range(len(data)), data, 1)[0]

    if slope > 0.1:
        return 'Increasing'
    elif slope < -0.1:
        return 'Decreasing'
    else:
        return 'Stable'


def main():
    """Main function to perform trend analysis on welfare data.
    """
    try:
        # Ensure the analysis directory exists
        if not os.path.exists(ANALYSIS_DIR):
            os.makedirs(ANALYSIS_DIR)

        # Load welfare data (replace with actual data loading mechanism)
        # This is just sample data for demonstration
        data = {
            'Date': pd.to_datetime(['2023-01-01', '2023-02-01', '2023-03-01', '2023-04-01', '2023-05-01', '2023-06-01', '2023-07-01', '2023-08-01', '2023-09-01', '2023-10-01']),
            'HealthIndicator1': [100, 102, 105, 103, 106, 108, 110, 112, 115, 113],
            'FoodPriceIndex': [150, 148, 145, 147, 150, 152, 155, 153, 151, 149],
            'EducationAccess': [75, 76, 77, 78, 79, 80, 81, 82, 83, 84]
        }
        df = pd.DataFrame(data)
        df = df.set_index('Date')

        # Key indicators for trend analysis
        indicators = ['HealthIndicator1', 'FoodPriceIndex', 'EducationAccess']

        # Perform trend analysis for each indicator
        results = {}
        for indicator in indicators:
            # Calculate moving average
            moving_average = calculate_moving_average(df[indicator])

            # Identify trend
            trend = identify_trend(df[indicator])

            # Store results
            results[indicator] = {
                'MovingAverage': moving_average,
                'Trend': trend
            }

        # Create a DataFrame from the results
        results_df = pd.DataFrame({
            indicator: results[indicator]['MovingAverage'] for indicator in indicators
        })
        results_df['Trend_HealthIndicator1'] = results['HealthIndicator1']['Trend']
        results_df['Trend_FoodPriceIndex'] = results['FoodPriceIndex']['Trend']
        results_df['Trend_EducationAccess'] = results['EducationAccess']['Trend']

        # Save results to CSV
        results_df.to_csv(TREND_ANALYSIS_FILE)

        print(f"Trend analysis completed and saved to {TREND_ANALYSIS_FILE}")

    except Exception as e:
        print(f"Error during trend analysis: {e}")


if __name__ == "__main__":
    main()