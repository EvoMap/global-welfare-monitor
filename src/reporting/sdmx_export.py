"""SDMX-CSV export for UN statistical data exchange.

Generates SDMX-CSV 2.0 compliant files from welfare indicator DataFrames.
Reference: https://sdmx.org/wp-content/uploads/SDMX-CSV-format-specification-v2.0.pdf
"""

import os
import logging
import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

SDMX_COLUMNS = [
    "DATAFLOW",
    "REF_AREA",
    "INDICATOR",
    "TIME_PERIOD",
    "OBS_VALUE",
    "UNIT_MEASURE",
    "OBS_STATUS",
]

DATAFLOW_ID = "EvoMap:GWM(1.0)"


def to_sdmx_csv(
    df,
    indicator_col="indicator",
    country_col="country",
    time_col="year",
    value_col="value",
    unit_col=None,
    output_path=None,
):
    """Convert a welfare data DataFrame to SDMX-CSV format.

    Args:
        df: Source DataFrame.
        indicator_col: Column name containing indicator codes.
        country_col: Column name containing ISO country codes.
        time_col: Column name containing time periods.
        value_col: Column name containing observation values.
        unit_col: Optional column name containing unit of measure.
        output_path: Optional path to write the CSV file.

    Returns:
        pd.DataFrame in SDMX-CSV format.
    """
    if df is None or df.empty:
        logger.warning("Empty DataFrame, cannot generate SDMX-CSV")
        return pd.DataFrame(columns=SDMX_COLUMNS)

    sdmx_df = pd.DataFrame()
    sdmx_df["DATAFLOW"] = [DATAFLOW_ID] * len(df)
    sdmx_df["REF_AREA"] = df[country_col].values if country_col in df.columns else ""
    sdmx_df["INDICATOR"] = df[indicator_col].values if indicator_col in df.columns else ""
    sdmx_df["TIME_PERIOD"] = df[time_col].values if time_col in df.columns else ""
    sdmx_df["OBS_VALUE"] = df[value_col].values if value_col in df.columns else ""

    if unit_col and unit_col in df.columns:
        sdmx_df["UNIT_MEASURE"] = df[unit_col].values
    else:
        sdmx_df["UNIT_MEASURE"] = ""

    sdmx_df["OBS_STATUS"] = "A"

    if output_path:
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        sdmx_df.to_csv(output_path, index=False)
        logger.info(f"SDMX-CSV written to {output_path} ({len(sdmx_df)} rows)")

    return sdmx_df
