"""Data ingestion pipeline orchestrator for the Global Welfare Monitor.

Coordinates data fetching from all sources (World Bank, WHO, GDACS, FAO, UNESCO),
runs analysis modules, and generates reports.
"""

import os
import sys
import logging
import traceback

DATA_DIR = os.environ.get("DATA_DIR", "/data")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("data_ingestion")


def _run_step(name, func):
    """Run a single ingestion step, log outcome, continue on failure."""
    try:
        logger.info(f"Starting: {name}")
        func()
        logger.info(f"Completed: {name}")
        return True
    except Exception:
        logger.error(f"Failed: {name}\n{traceback.format_exc()}")
        return False


def ingest_world_bank():
    from src.world_bank_data_ingestion import main as wb_main
    wb_main()


def ingest_who():
    from src.who_api_ingestion import main as who_main
    who_main()


def ingest_gdacs():
    from src.gdacs_disaster_alerts import fetch_gdacs_alerts, save_alerts_to_csv
    alerts = fetch_gdacs_alerts()
    if alerts:
        save_alerts_to_csv(alerts)


def ingest_fao():
    from src.fao_food_prices import main as fao_main
    fao_main()


def ingest_unesco():
    from src.unesco_education import main as unesco_main
    unesco_main()


def run_analysis():
    from src.trend_analysis import main as trend_main
    trend_main()


PIPELINE_STEPS = [
    ("World Bank economic indicators", ingest_world_bank),
    ("WHO health indicators", ingest_who),
    ("GDACS disaster alerts", ingest_gdacs),
    ("FAO food prices", ingest_fao),
    ("UNESCO education data", ingest_unesco),
    ("Trend analysis", run_analysis),
]


def ingest_data(steps=None):
    """Run the full ingestion pipeline.

    Args:
        steps: Optional list of (name, callable) tuples. Defaults to PIPELINE_STEPS.
    """
    os.makedirs(DATA_DIR, exist_ok=True)

    pipeline = steps if steps is not None else PIPELINE_STEPS
    results = {}
    for name, func in pipeline:
        results[name] = _run_step(name, func)

    succeeded = sum(1 for v in results.values() if v)
    total = len(results)
    logger.info(f"Pipeline complete: {succeeded}/{total} steps succeeded")

    failed = [name for name, ok in results.items() if not ok]
    if failed:
        logger.warning(f"Failed steps: {', '.join(failed)}")

    return results


if __name__ == "__main__":
    ingest_data()
