"""Ingests health indicators from the WHO Global Health Observatory (GHO) API.

Handles pagination via OData @odata.nextLink and retries on transient failures.
Stores results in data/who/health_indicators.csv.
"""

import os
import time
import logging
import requests
import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

BASE_URL = "https://ghoapi.azureedge.net/api"
INDICATORS = [
    "WHOSIS_000001",
    "MDG_0000000001",
    "WHS9_95",
    "WHS7_104",
    "AIR_000004",
]
OUTPUT_DIR = "data/who"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "health_indicators.csv")

MAX_RETRIES = 3
RETRY_BACKOFF = 2


def fetch_data(indicator_code, max_retries=MAX_RETRIES):
    """Fetches data for a specific indicator with retry and pagination support."""
    url = f"{BASE_URL}/{indicator_code}"
    all_data = []

    for attempt in range(1, max_retries + 1):
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            data = response.json()
            all_data.extend(data.get("value", []))

            next_link = data.get("@odata.nextLink")
            while next_link:
                response = requests.get(next_link, timeout=30)
                response.raise_for_status()
                data = response.json()
                all_data.extend(data.get("value", []))
                next_link = data.get("@odata.nextLink")

            return all_data

        except requests.exceptions.RequestException as e:
            logger.warning(f"Attempt {attempt}/{max_retries} failed for {indicator_code}: {e}")
            if attempt < max_retries:
                time.sleep(RETRY_BACKOFF ** attempt)
            else:
                logger.error(f"All {max_retries} attempts failed for {indicator_code}")
                return None


def main():
    """Fetch data for all indicators and save to CSV."""
    all_indicators_data = []

    for indicator in INDICATORS:
        logger.info(f"Fetching {indicator}...")
        data = fetch_data(indicator)
        if data:
            for record in data:
                record["indicator"] = indicator
            all_indicators_data.extend(data)
        else:
            logger.warning(f"No data returned for {indicator}")

    if not all_indicators_data:
        logger.error("No data fetched from any indicator. Exiting.")
        return

    df = pd.DataFrame(all_indicators_data)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    try:
        df.to_csv(OUTPUT_FILE, index=False)
        logger.info(f"Data saved to {OUTPUT_FILE} ({len(df)} rows)")
    except Exception as e:
        logger.error(f"Error saving to CSV: {e}")


if __name__ == "__main__":
    main()
