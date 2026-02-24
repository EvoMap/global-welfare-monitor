"""Module for cleaning and transforming welfare data from WHO and World Bank.

This script handles missing values, data type conversions, and unit conversions
to create a unified dataset for the Global Welfare Monitor project.
"""

import pandas as pd
import numpy as np
import os


def clean_and_transform_data(who_data_path, world_bank_data_path, output_path):
    """Cleans and transforms data from WHO and World Bank, and saves it to a CSV file.

    Args:
        who_data_path (str): Path to the WHO data CSV file.
        world_bank_data_path (str): Path to the World Bank data CSV file.
        output_path (str): Path to save the cleaned and transformed data.
    """
    try:
        # Load data
        who_data = pd.read_csv(who_data_path)
        world_bank_data = pd.read_csv(world_bank_data_path)

        # Data Cleaning and Transformation
        # 1. Handle missing values (replace with NaN, then impute with mean/median)
        who_data.replace(["", "NA", "N/A"], np.nan, inplace=True)
        world_bank_data.replace(["", "NA", "N/A"], np.nan, inplace=True)

        # Impute missing values (example: using the mean for numerical columns)
        for col in who_data.columns:
            if pd.api.types.is_numeric_dtype(who_data[col]):
                who_data[col].fillna(who_data[col].mean(), inplace=True)
        for col in world_bank_data.columns:
            if pd.api.types.is_numeric_dtype(world_bank_data[col]):
                world_bank_data[col].fillna(world_bank_data[col].mean(), inplace=True)

        # 2. Data type conversions (example: converting columns to numeric)
        for col in who_data.columns:
            try:
                who_data[col] = pd.to_numeric(who_data[col])
            except ValueError:
                pass  # Ignore columns that cannot be converted to numeric
        for col in world_bank_data.columns:
            try:
                world_bank_data[col] = pd.to_numeric(world_bank_data[col])
            except ValueError:
                pass  # Ignore columns that cannot be converted to numeric

        # 3. Unit conversions (example: converting temperature from Celsius to Fahrenheit - placeholder)
        # This section would contain specific unit conversion logic based on the data
        # For example:
        # if 'temperature_celsius' in who_data.columns:
        #     who_data['temperature_fahrenheit'] = who_data['temperature_celsius'] * 9/5 + 32

        # 4. Standardize column names (example: converting to lowercase and replacing spaces with underscores)
        who_data.columns = [col.lower().replace(" ", "_") for col in who_data.columns]
        world_bank_data.columns = [col.lower().replace(" ", "_") for col in world_bank_data.columns]

        # 5. Merge the datasets (example: using a common column like 'country')
        # Ensure both datasets have a common column for merging
        if 'country' in who_data.columns and 'country' in world_bank_data.columns:
            welfare_data = pd.merge(who_data, world_bank_data, on='country', how='outer')
        else:
            print("Warning: No common 'country' column found for merging. Concatenating datasets.")
            welfare_data = pd.concat([who_data, world_bank_data], axis=0, ignore_index=True)

        # Save the cleaned and transformed data to a CSV file
        welfare_data.to_csv(output_path, index=False)

        print(f"Cleaned and transformed data saved to {output_path}")

    except FileNotFoundError as e:
        print(f"Error: File not found: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    # Example usage:
    # Define paths to your data files
    who_data_path = "data/raw/who_data.csv"  # Replace with your actual path
    world_bank_data_path = "data/raw/world_bank_data.csv"  # Replace with your actual path
    output_path = "data/processed/welfare_data.csv"

    # Create the directories if they don't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    os.makedirs(os.path.dirname(who_data_path), exist_ok=True)
    os.makedirs(os.path.dirname(world_bank_data_path), exist_ok=True)

    # Create dummy data files if they don't exist
    if not os.path.exists(who_data_path):
        pd.DataFrame({'country': ['USA', 'Canada'], 'life_expectancy': [78, 82], 'population': [330000000, 38000000]}).to_csv(who_data_path, index=False)
    if not os.path.exists(world_bank_data_path):
        pd.DataFrame({'country': ['USA', 'Canada'], 'gdp': [21000000, 1700000], 'unemployment_rate': [4.0, 6.0]}).to_csv(world_bank_data_path, index=False)

    clean_and_transform_data(who_data_path, world_bank_data_path, output_path)
