"""Fetches global food price data from the FAO Data API (BigQuery backend).

Uses the FAO catalog BigQuery endpoint for Consumer Price Indices (CP domain).
Parses data into a standardized DataFrame and stores results in data/fao_food_prices.csv.
"""

import os
import io
import time
import logging
import pandas as pd
import requests

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

DATA_DIR = "data"
OUTPUT_FILE = os.path.join(DATA_DIR, "fao_food_prices.csv")

FAO_BIGQUERY_URL = (
    "https://api.data.apps.fao.org/api/v2/bigquery"
    "?sql_url=https%3A%2F%2Fdata.apps.fao.org%2Fcatalog%2Fdataset%2F"
    "040d6f83-9372-4e0c-8809-7c33162eb5c7%2Fresource%2F"
    "80ba0114-b0c4-487f-bf1a-772ac88efb74%2Fdownload%2F"
    "prices-cp-query.sql"
    "&item_code={item_code}&output_format=csv"
)

FOOD_CPI_ITEM_CODE = "23013"

MAX_RETRIES = 3
RETRY_BACKOFF = 2


def fetch_fao_food_prices(item_code=FOOD_CPI_ITEM_CODE, max_retries=MAX_RETRIES):
    """Fetches food price data from FAO BigQuery API."""
    url = FAO_BIGQUERY_URL.format(item_code=item_code)
    for attempt in range(1, max_retries + 1):
        try:
            logger.info(f"Downloading FAO food CPI data (attempt {attempt})...")
            resp = requests.get(url, timeout=120)
            resp.raise_for_status()
            df = pd.read_csv(io.StringIO(resp.text), low_memory=False)
            logger.info(f"Downloaded {len(df)} rows from FAO")
            return df
        except Exception as e:
            logger.warning(f"Attempt {attempt}/{max_retries} failed: {e}")
            if attempt < max_retries:
                time.sleep(RETRY_BACKOFF ** attempt)
            else:
                logger.error(f"All {max_retries} download attempts failed")
                return None


def standardize_data(df):
    """Standardizes column names and selects relevant columns."""
    try:
        rename_map = {}
        for col in df.columns:
            col_lower = col.strip().lower()
            if col_lower in ("country_name_en", "area"):
                rename_map[col] = "country"
            elif col_lower == "item":
                rename_map[col] = "indicator"
            elif col_lower == "date":
                rename_map[col] = "date"
            elif col_lower == "year" and "date" not in [c.strip().lower() for c in df.columns]:
                rename_map[col] = "date"
            elif col_lower == "value":
                rename_map[col] = "value"
            elif col_lower in ("unit", "flag_description"):
                rename_map[col] = col_lower

        df = df.rename(columns=rename_map)

        if "country" not in df.columns:
            logger.error(f"Missing 'country' column. Available: {list(df.columns)}")
            return None

        if "date" not in df.columns and "year" in df.columns:
            df = df.rename(columns={"year": "date"})

        required = ["country", "date", "value"]
        missing = [c for c in required if c not in df.columns]
        if missing:
            logger.error(f"Missing required columns after rename: {missing}")
            logger.info(f"Available columns: {list(df.columns)}")
            return None

        keep = [c for c in ["country", "indicator", "date", "value"] if c in df.columns]
        df = df[keep].copy()
        df["value"] = pd.to_numeric(df["value"], errors="coerce")
        df = df.dropna(subset=["value"])

        return df
    except Exception as e:
        logger.error(f"Error standardizing data: {e}")
        return None


def save_data(df, output_file=OUTPUT_FILE):
    """Saves the DataFrame to a CSV file."""
    try:
        os.makedirs(DATA_DIR, exist_ok=True)
        df.to_csv(output_file, index=False)
        logger.info(f"Data saved to {output_file} ({len(df)} rows)")
    except OSError as e:
        logger.error(f"Error saving data: {e}")


def main():
    """Fetch, standardize, and save FAO food price data."""
    df = fetch_fao_food_prices()
    if df is not None:
        df = standardize_data(df)
        if df is not None:
            save_data(df)


if __name__ == "__main__":
    main()
