"""HXL (Humanitarian Exchange Language) tagged CSV export for HDX platform.

Generates CSVs with HXL hashtag row as required by the
Humanitarian Data Exchange (HDX) platform.
Reference: https://hxlstandard.org/
"""

import os
import logging
import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

DEFAULT_HXL_TAGS = {
    "country": "#country+name",
    "country_code": "#country+code",
    "region": "#region+name",
    "year": "#date+year",
    "date": "#date",
    "indicator": "#indicator+name",
    "value": "#indicator+value+num",
    "unit": "#indicator+unit",
    "event_type": "#event+type",
    "severity": "#severity+text",
    "description": "#description",
    "coordinates": "#geo+coord",
    "population": "#population+num",
    "phase": "#severity+num",
    "price": "#value+price",
    "caloric_deficit_percentage": "#indicator+value+num",
    "price_volatility": "#indicator+value+num",
    "composite_index": "#indicator+value+num",
    "rank": "#indicator+rank+num",
}


def to_hxl_csv(df, output_path, hxl_tags=None):
    """Write a DataFrame to CSV with an HXL hashtag row.

    Args:
        df: Source DataFrame.
        output_path: Path to write the HXL-tagged CSV.
        hxl_tags: Optional dict mapping column names to HXL tags.
                  Columns without a mapping get an empty tag.

    Returns:
        Path to the written file.
    """
    if df is None or df.empty:
        logger.warning("Empty DataFrame, cannot generate HXL-CSV")
        return None

    tags = hxl_tags or DEFAULT_HXL_TAGS
    tag_row = {col: tags.get(col, "") for col in df.columns}

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        header = ",".join(df.columns)
        f.write(header + "\n")
        hxl_line = ",".join(tag_row[col] for col in df.columns)
        f.write(hxl_line + "\n")

    df.to_csv(output_path, mode="a", header=False, index=False)
    logger.info(f"HXL-CSV written to {output_path} ({len(df)} rows)")
    return output_path
