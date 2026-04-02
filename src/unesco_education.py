"""Fetches education access metrics from the UNESCO Institute for Statistics (UIS) API.

Uses the UIS Data API v1 (api.uis.unesco.org/api/public/).
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

UIS_API_BASE = "https://api.uis.unesco.org/api/public"


class UNESCOEducationData:
    """Fetches, processes, and saves UNESCO education data."""

    def __init__(self, api_url=UIS_API_BASE):
        self.api_url = api_url.rstrip("/")
        self.data = None

    def fetch_data(self, endpoint, params=None):
        """Fetches data from the UNESCO UIS API with retry."""
        url = f"{self.api_url}/{endpoint}"
        headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
        }
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                response = requests.get(url, params=params, headers=headers, timeout=60)
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
        """Retrieves education data from the UNESCO UIS API v1."""
        indicators = {
            "GER.1": "Gross Enrollment Ratio, Primary",
            "LR.AG15T99": "Adult Literacy Rate (15+)",
            "OFST.1.CP": "Out-of-School Children, Primary",
        }

        indicator_codes = list(indicators.keys())
        params = [("indicator", code) for code in indicator_codes]

        logger.info(f"Fetching {len(indicator_codes)} indicators from UIS API...")
        data = self.fetch_data("data/indicators", params=params)

        if not data:
            logger.warning("No response from UIS API.")
            return None

        records = data.get("records", [])
        if not records:
            logger.warning("UIS API returned zero records.")
            return None

        all_data = []
        for rec in records:
            indicator_id = rec.get("indicatorId", "")
            indicator_name = indicators.get(indicator_id, indicator_id)
            geo_unit = rec.get("geoUnit", "")
            year = rec.get("year")
            value = rec.get("value")

            if geo_unit and year is not None and value is not None:
                all_data.append({
                    "Country": geo_unit,
                    "Year": year,
                    "Indicator": indicator_name,
                    "Value": value,
                })

        if not all_data:
            logger.warning("No education data retrieved from UNESCO API.")
            return None

        df = pd.DataFrame(all_data)
        logger.info(f"Retrieved {len(df)} education data records from UIS API")
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
