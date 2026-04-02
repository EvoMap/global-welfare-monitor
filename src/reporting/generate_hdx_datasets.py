"""Generate HXL-tagged datasets ready for HDX upload.

Reads ingested data files and produces HXL-tagged CSVs in reports/hdx/.
"""

import os
import logging
import pandas as pd
from src.reporting.hxl_export import to_hxl_csv

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

DATA_DIR = os.environ.get("DATA_DIR", "data")
HDX_OUTPUT_DIR = os.path.join("reports", "hdx")


def _try_read_csv(path):
    if not os.path.exists(path):
        logger.warning(f"File not found: {path}")
        return None
    try:
        return pd.read_csv(path)
    except Exception as e:
        logger.error(f"Error reading {path}: {e}")
        return None


def generate_all():
    """Generate HXL-tagged CSVs for all available datasets."""
    os.makedirs(HDX_OUTPUT_DIR, exist_ok=True)
    generated = []

    wb_path = os.path.join(DATA_DIR, "world_bank", "economic_indicators.csv")
    df = _try_read_csv(wb_path)
    if df is not None:
        out = os.path.join(HDX_OUTPUT_DIR, "global-economic-indicators.hxl.csv")
        to_hxl_csv(df, out)
        generated.append(out)

    who_path = os.path.join(DATA_DIR, "who", "health_indicators.csv")
    df = _try_read_csv(who_path)
    if df is not None:
        out = os.path.join(HDX_OUTPUT_DIR, "global-health-indicators.hxl.csv")
        to_hxl_csv(df, out)
        generated.append(out)

    gdacs_path = os.path.join(DATA_DIR, "gdacs_alerts.csv")
    df = _try_read_csv(gdacs_path)
    if df is not None:
        out = os.path.join(HDX_OUTPUT_DIR, "disaster-alerts.hxl.csv")
        to_hxl_csv(df, out)
        generated.append(out)

    fao_path = os.path.join(DATA_DIR, "fao_food_prices.csv")
    df = _try_read_csv(fao_path)
    if df is not None:
        out = os.path.join(HDX_OUTPUT_DIR, "food-price-indices.hxl.csv")
        to_hxl_csv(df, out)
        generated.append(out)

    logger.info(f"Generated {len(generated)} HXL datasets in {HDX_OUTPUT_DIR}")
    return generated


if __name__ == "__main__":
    generate_all()
