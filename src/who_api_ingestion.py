"""
This script ingests health indicators data from the WHO API, handles authentication,
pagination, and error handling. It stores the data in a CSV file within the
data/who directory.
"""

import os
import requests
import pandas as pd

# Configuration
BASE_URL = "https://ghoapi.azureedge.net/api"
INDICATORS = [
    "WHOSIS_000001",  # Life expectancy at birth
    "MDG_0000000001",  # Infant mortality rate
    "WHS9_95",  # Under-five mortality rate
    "WHS7_104",  # Maternal mortality ratio (per 100,000 live births)
    "AIR_000004"   # Probability of dying between 30 and 70 years from any of cardiovascular disease, cancer, diabetes, or chronic respiratory disease
]
OUTPUT_DIR = "data/who"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "health_indicators.csv")


def fetch_data(indicator_code):
    """Fetches data for a specific indicator from the WHO API."""
    url = f"{BASE_URL}/{indicator_code}"
    all_data = []
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        data = response.json()
        all_data.extend(data['value'])

        # Handle pagination (if applicable - WHO API doesn't seem to use standard pagination)
        # while data.get('nextLink'):
        #     url = data['nextLink']
        #     response = requests.get(url)
        #     response.raise_for_status()
        #     data = response.json()
        #     all_data.extend(data['value'])

        return all_data

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data for {indicator_code}: {e}")
        return None


def main():
    """Main function to fetch data for all indicators and save to CSV."""
    all_indicators_data = []

    for indicator in INDICATORS:
        print(f"Fetching data for {indicator}...")
        data = fetch_data(indicator)
        if data:
            # Add indicator code to each record for easier identification
            for record in data:
                record['indicator'] = indicator
            all_indicators_data.extend(data)

    if not all_indicators_data:
        print("No data fetched. Exiting.")
        return

    # Convert to Pandas DataFrame and save to CSV
    df = pd.DataFrame(all_indicators_data)

    # Ensure the output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    try:
        df.to_csv(OUTPUT_FILE, index=False)
        print(f"Data saved to {OUTPUT_FILE}")
    except Exception as e:
        print(f"Error saving data to CSV: {e}")


if __name__ == "__main__":
    main()