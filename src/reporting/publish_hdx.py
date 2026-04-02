"""Publish datasets to the Humanitarian Data Exchange (HDX) platform.

Uses hdx-python-api to create/update datasets on HDX.
Requires HDX_API_KEY environment variable to be set.

Dataset registration: https://data.humdata.org/
API docs: https://hdx-python-api.readthedocs.io/
"""

import os
import sys
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

HDX_OUTPUT_DIR = os.path.join("reports", "hdx")
ORG_NAME = "evomap"

DATASETS = [
    {
        "name": "evomap-global-economic-indicators",
        "title": "Global Economic Indicators (World Bank)",
        "file": "global-economic-indicators.hxl.csv",
        "notes": (
            "GDP per capita, poverty headcount, population, school enrollment, "
            "and health expenditure data sourced from the World Bank API. "
            "Updated weekly by the EvoMap Global Welfare Monitor pipeline."
        ),
        "tags": ["economics", "gdp", "poverty", "world bank"],
    },
    {
        "name": "evomap-global-health-indicators",
        "title": "Global Health Indicators (WHO GHO)",
        "file": "global-health-indicators.hxl.csv",
        "notes": (
            "Life expectancy, infant mortality, under-five mortality, maternal mortality, "
            "and NCD mortality data sourced from the WHO Global Health Observatory API. "
            "Updated weekly by the EvoMap Global Welfare Monitor pipeline."
        ),
        "tags": ["health", "mortality", "who", "life expectancy"],
    },
    {
        "name": "evomap-disaster-alerts",
        "title": "Global Disaster Alerts (GDACS)",
        "file": "disaster-alerts.hxl.csv",
        "notes": (
            "Real-time earthquake, flood, cyclone, and drought alerts "
            "from the Global Disaster Alert and Coordination System RSS feed. "
            "Updated weekly by the EvoMap Global Welfare Monitor pipeline."
        ),
        "tags": ["disasters", "earthquakes", "floods", "alerts"],
    },
    {
        "name": "evomap-food-price-indices",
        "title": "Global Food Price Indices (FAO)",
        "file": "food-price-indices.hxl.csv",
        "notes": (
            "Consumer food price indices sourced from FAOSTAT. "
            "Updated weekly by the EvoMap Global Welfare Monitor pipeline."
        ),
        "tags": ["food", "prices", "fao", "food security"],
    },
]


def publish():
    """Create or update datasets on HDX."""
    api_key = os.environ.get("HDX_API_KEY")
    hdx_site = os.environ.get("HDX_SITE", "stage")
    org_name = os.environ.get("HDX_ORG_NAME", ORG_NAME)

    if not api_key:
        logger.error("HDX_API_KEY environment variable not set. Aborting.")
        sys.exit(1)

    try:
        from hdx.api.configuration import Configuration
        from hdx.data.dataset import Dataset
        from hdx.data.resource import Resource
    except ImportError:
        logger.error("hdx-python-api not installed. Run: pip install hdx-python-api")
        sys.exit(1)

    Configuration.create(
        hdx_site=hdx_site,
        user_agent="EvoMap/GlobalWelfareMonitor",
        hdx_key=api_key,
    )

    for ds_config in DATASETS:
        filepath = os.path.join(HDX_OUTPUT_DIR, ds_config["file"])
        if not os.path.exists(filepath):
            logger.warning(f"Skipping {ds_config['name']}: {filepath} not found")
            continue

        try:
            existing = Dataset.read_from_hdx(ds_config["name"])
        except Exception:
            existing = None

        if existing:
            logger.info(f"Updating existing dataset: {ds_config['name']}")
            resources = existing.get_resources()
            if resources:
                resources[0].set_file_to_upload(filepath)
            existing.update_in_hdx()
        else:
            logger.info(f"Creating new dataset: {ds_config['name']}")
            dataset = Dataset({
                "name": ds_config["name"],
                "title": ds_config["title"],
                "notes": ds_config["notes"],
                "owner_org": org_name,
                "maintainer": org_name,
                "dataset_source": "EvoMap Global Welfare Monitor",
                "methodology": "Registry",
                "license_id": "cc-by",
                "data_update_frequency": "7",
                "subnational": "0",
            })

            for tag in ds_config["tags"]:
                dataset.add_tag(tag)

            dataset.set_expected_update_frequency("Every week")

            resource = Resource({
                "name": ds_config["file"],
                "description": ds_config["title"],
                "format": "csv",
            })
            resource.set_file_to_upload(filepath)
            dataset.add_update_resource(resource)

            try:
                dataset.create_in_hdx(allow_no_resources=False)
                logger.info(f"Created dataset: {ds_config['name']}")
            except Exception as e:
                logger.error(f"Failed to create {ds_config['name']}: {e}")

    logger.info("HDX publishing complete")


if __name__ == "__main__":
    publish()
