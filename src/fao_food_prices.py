"""Fetches global food price data from the FAOSTAT API.

Uses the FAOSTAT bulk download endpoint for Consumer Price Indices (CP domain).
Parses data into a standardized DataFrame and stores results in data/fao_food_prices.csv.
"""

import os
import time
import logging
import pandas as pd
import requests

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

DATA_DIR = "data"
OUTPUT_FILE = os.path.join(DATA_DIR, "fao_food_prices.csv")
FAOSTAT_BULK_URL = "https://fenixservices.fao.org/faostat/static/bulkdownloads/ConsumerPriceIndices_E_All_Data_NOFLAG.csv.zip"
MAX_RETRIES = 3
RETRY_BACKOFF = 2


def fetch_fao_food_prices(url=FAOSTAT_BULK_URL, max_retries=MAX_RETRIES):
    """Fetches food price data from FAOSTAT bulk download."""
    for attempt in range(1, max_retries + 1):
        try:
            logger.info(f"Downloading FAOSTAT data (attempt {attempt})...")
            df = pd.read_csv(url, encoding="latin-1", low_memory=False)
            logger.info(f"Downloaded {len(df)} rows from FAOSTAT")
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
            if col_lower == "area":
                rename_map[col] = "country"
            elif col_lower == "item":
                rename_map[col] = "indicator"
            elif col_lower == "year":
                rename_map[col] = "date"
            elif col_lower == "value":
                rename_map[col] = "value"
            elif col_lower == "unit":
                rename_map[col] = "unit"

        df = df.rename(columns=rename_map)

        required = ["country", "indicator", "date", "value"]
        missing = [c for c in required if c not in df.columns]
        if missing:
            logger.error(f"Missing required columns after rename: {missing}")
            logger.info(f"Available columns: {list(df.columns)}")
            return None

        keep = [c for c in ["country", "indicator", "date", "value", "unit"] if c in df.columns]
        df = df[keep].copy()
        df["value"] = pd.to_numeric(df["value"], errors="coerce")
        df = df.dropna(subset=["value"])

        if df["value"].isnull().any():
            logger.warning("Missing values in 'value' column after coercion")

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
