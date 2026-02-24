"""
This script ingests economic indicators data from the World Bank API,
handles API authentication, pagination, and error handling. It stores
the data in a CSV format within the `data/world_bank` directory.
"""

import wbgapi as wb
import pandas as pd
import os

def fetch_world_bank_data(indicators, countries='all', mrnev=1):
    """
    Fetches data from the World Bank API for specified indicators and countries.

    Args:
        indicators (list): A list of World Bank indicator codes.
        countries (str): A string representing the countries to fetch data for. Defaults to 'all'.
        mrnev (int): Most Recent N Values to return. Defaults to 1.

    Returns:
        pandas.DataFrame: A DataFrame containing the fetched data.
    """
    try:
        data = wb.data.DataFrame(indicators, countries, mrnev=mrnev, numericTimeKeys=True)
        data = data.stack().unstack(level=1)
        data.index.names = ['country', 'year']
        data = data.reset_index()
        return data
    except Exception as e:
        print(f"Error fetching data from World Bank API: {e}")
        return None


def save_data_to_csv(data, filepath):
    """
    Saves the data to a CSV file.

    Args:
        data (pandas.DataFrame): The DataFrame to save.
        filepath (str): The path to the CSV file.
    """
    try:
        data.to_csv(filepath, index=False)
        print(f"Data saved to {filepath}")
    except Exception as e:
        print(f"Error saving data to CSV: {e}")



def main():
    """
    Main function to execute the data ingestion process.
    """
    indicators = [
        'NY.GDP.PCAP.CD',  # GDP per capita (current US$)
        'SI.POV.DDAY',     # Poverty headcount ratio at $2.15 a day (2017 PPP) (% of population)
        'SP.POP.TOTL',     # Total population
        'SE.PRM.ENRR',     # School enrollment, primary (% gross)
        'SH.XPD.CHEX.GD.ZS' # Current health expenditure (% of GDP)
    ]

    data = fetch_world_bank_data(indicators)

    if data is not None:
        # Ensure the directory exists
        output_dir = 'data/world_bank'
        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, 'economic_indicators.csv')
        save_data_to_csv(data, filepath)


if __name__ == "__main__":
    main()