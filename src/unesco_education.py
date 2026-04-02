"""Fetches education access metrics from the UNESCO Institute for Statistics (UIS) API.

Retrieves enrollment rates, literacy rates, and out-of-school children counts by country.
Parses data into a standardized DataFrame, validates, and saves to data/unesco_education.csv.
"""

import os
import time
import logging
import pandas as pd
import requests

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

MAX_RETRIES = 3
RETRY_BACKOFF = 2


class UNESCOEducationData:
    """Fetches, processes, and saves UNESCO education data."""

    def __init__(self, api_url="http://api.uis.unesco.org/"):
        self.api_url = api_url
        self.data = None

    def fetch_data(self, endpoint, params=None):
        """Fetches data from the UNESCO API with retry."""
        url = f"{self.api_url}{endpoint}"
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                response = requests.get(url, params=params, timeout=30)
                response.raise_for_status()
                return response.json()
            except requests.exceptions.RequestException as e:
                logger.warning(f"Attempt {attempt}/{MAX_RETRIES} for {endpoint}: {e}")
                if attempt < MAX_RETRIES:
                    time.sleep(RETRY_BACKOFF ** attempt)
                else:
                    logger.error(f"All {MAX_RETRIES} attempts failed for {endpoint}")
                    return None

    def get_education_data(self):
        """Retrieves education data from the UNESCO API."""
        indicators = {
            "UIS.NERA.1": "Enrollment Rate, Primary",
            "UIS.LIT.A": "Literacy Rate, Adult",
            "UIS.OOSC.1": "Out-of-School Children, Primary",
        }
        all_data = []
        for indicator_code, indicator_name in indicators.items():
            data = self.fetch_data("data", params={"indicator": indicator_code, "format": "json"})
            if data:
                for item in data:
                    try:
                        country = item.get("country")
                        year = item.get("year")
                        value = item.get("value")
                        if country and year and value is not None:
                            all_data.append({
                                "Country": country,
                                "Year": year,
                                "Indicator": indicator_name,
                                "Value": value,
                            })
                    except (TypeError, ValueError) as e:
                        logger.warning(f"Skipping invalid data point: {item}. Error: {e}")
            else:
                logger.warning(f"No data received for indicator: {indicator_code}")

        if not all_data:
            logger.warning("No education data retrieved from UNESCO API.")
            return None

        df = pd.DataFrame(all_data)
        self.data = df
        return df

    def validate_data(self, df):
        """Validates the data for missing values and data types."""
        if df.isnull().sum().sum() > 0:
            logger.error("Data contains missing values.")
            return False
        if not pd.api.types.is_numeric_dtype(df["Value"]):
            logger.error("Value column is not numeric.")
            return False
        return True

    def save_data(self, df, filepath="data/unesco_education.csv"):
        """Saves the DataFrame to a CSV file."""
        try:
            os.makedirs(os.path.dirname(filepath) or ".", exist_ok=True)
            df.to_csv(filepath, index=False)
            logger.info(f"UNESCO education data saved to {filepath}")
        except Exception as e:
            logger.error(f"Error saving data to CSV: {e}")


def main():
    education_data = UNESCOEducationData()
    df = education_data.get_education_data()
    if df is not None:
        if education_data.validate_data(df):
            education_data.save_data(df)
        else:
            logger.error("Data validation failed. Data not saved.")
    else:
        logger.error("Failed to retrieve education data.")


if __name__ == "__main__":
    main()
