"""
This script performs anomaly detection on welfare data using the Isolation Forest algorithm.
It identifies anomalies in key indicators and saves the results to a CSV file.
"""

import pandas as pd
from sklearn.ensemble import IsolationForest
import os

def detect_anomalies(data_path, output_path, indicators):
    """
    Detects anomalies in specified indicators using Isolation Forest.

    Args:
        data_path (str): Path to the welfare data CSV file.
        output_path (str): Path to save the anomaly detection results.
        indicators (list): List of key indicators to analyze.

    Returns:
        None. Saves the anomaly detection results to a CSV file.
    """
    try:
        # Load the data
        df = pd.read_csv(data_path)

        # Check if the specified indicators exist in the DataFrame
        for indicator in indicators:
            if indicator not in df.columns:
                raise ValueError(f"Indicator '{indicator}' not found in the data.")

        # Anomaly detection using Isolation Forest
        for indicator in indicators:
            # Handle missing values by filling with the mean
            df[indicator] = df[indicator].fillna(df[indicator].mean())

            # Train the Isolation Forest model
            model = IsolationForest(contamination='auto', random_state=42)
            model.fit(df[[indicator]])

            # Predict anomalies
            df[f'{indicator}_anomaly'] = model.predict(df[[indicator]])

        # Save the anomaly detection results
        output_dir = os.path.dirname(output_path)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        df.to_csv(output_path, index=False)

        print(f"Anomaly detection completed. Results saved to {output_path}")

    except FileNotFoundError:
        print(f"Error: Data file not found at {data_path}")
    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    # Example usage
    DATA_PATH = 'data/welfare_data.csv'
    OUTPUT_PATH = 'data/analysis/anomaly_detection.csv'
    KEY_INDICATORS = ['Health_Index', 'Food_Price_Index', 'Education_Access']

    # Create a dummy welfare_data.csv for testing
    if not os.path.exists('data'):
        os.makedirs('data')
    if not os.path.exists(DATA_PATH):
        dummy_data = {
            'Health_Index': [70, 72, 75, 68, 90, 71, 73, 69, 74, 76],
            'Food_Price_Index': [110, 112, 115, 108, 130, 111, 113, 109, 114, 116],
            'Education_Access': [80, 82, 85, 78, 95, 81, 83, 79, 84, 86],
            'Disaster_Alerts': [5, 6, 7, 4, 8, 5, 6, 4, 7, 9]
        }
        dummy_df = pd.DataFrame(dummy_data)
        dummy_df.to_csv(DATA_PATH, index=False)

    detect_anomalies(DATA_PATH, OUTPUT_PATH, KEY_INDICATORS)
