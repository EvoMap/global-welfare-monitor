"""
Fetches global food price data from the FAO Food Price Monitoring and Analysis (FPMA) API or FAOSTAT.
Parses the data into a standardized DataFrame with columns: country, indicator, date, value, unit.
Stores results in data/fao_food_prices.csv.
Includes error handling and data validation.
"""

import pandas as pd
import requests
import os

DATA_DIR = 'data'
OUTPUT_FILE = os.path.join(DATA_DIR, 'fao_food_prices.csv')

# FAOSTAT API endpoint (example, may need adjustment based on specific data requirements)
FAOSTAT_API_URL = 'http://fenixservices.fao.org/faostat/api/v1/en/data/CP'


def fetch_fao_food_prices(api_url=FAOSTAT_API_URL):
    """Fetches food price data from the FAOSTAT API.

    Args:
        api_url (str): The URL of the FAOSTAT API.

    Returns:
        pandas.DataFrame: A DataFrame containing the fetched data, or None if an error occurred.
    """
    try:
        response = requests.get(api_url)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        data = response.json()['data']
        return pd.DataFrame(data)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from FAOSTAT API: {e}")
        return None
    except KeyError as e:
        print(f"Error parsing JSON response: Missing key {e}")
        return None


def standardize_data(df):
    """Standardizes the DataFrame to the required format.

    Args:
        df (pandas.DataFrame): The DataFrame to standardize.

    Returns:
        pandas.DataFrame: The standardized DataFrame.
    """
    try:
        # Rename columns (example, adjust based on actual column names)
        df = df.rename(columns={
            'Area': 'country',
            'Item': 'indicator',
            'Year': 'date',
            'Value': 'value',
            'Unit': 'unit'
        })

        # Select relevant columns
        df = df[['country', 'indicator', 'date', 'value', 'unit']]

        # Convert date to datetime objects
        df['date'] = pd.to_datetime(df['date'], format='%Y')

        # Data validation (example)
        if df['value'].isnull().any():
            print("Warning: Missing values in 'value' column.")

        return df
    except KeyError as e:
        print(f"Error: Required column not found: {e}")
        return None
    except ValueError as e:
        print(f"Error converting data: {e}")
        return None


def save_data(df, output_file=OUTPUT_FILE):
    """Saves the DataFrame to a CSV file.

    Args:
        df (pandas.DataFrame): The DataFrame to save.
        output_file (str): The path to the output CSV file.
    """
    try:
        # Ensure the data directory exists
        os.makedirs(DATA_DIR, exist_ok=True)
        df.to_csv(output_file, index=False)
        print(f"Data saved to {output_file}")
    except OSError as e:
        print(f"Error saving data to file: {e}")





def main():
    """Main function to fetch, standardize, and save FAO food price data."""
    df = fetch_fao_food_prices()
    if df is not None:
        df = standardize_data(df)
        if df is not None:
            save_data(df)


if __name__ == "__main__":
    main()