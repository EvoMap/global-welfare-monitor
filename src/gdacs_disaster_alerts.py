"""Fetches real-time disaster alerts from GDACS RSS feed.

Parses earthquake, flood, cyclone, and drought events.
Standardizes output and saves to data/gdacs_alerts.csv with deduplication.
"""

import os
import time
import logging
from datetime import datetime

import feedparser
import pandas as pd
import requests

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

GDACS_RSS_URL = "https://www.gdacs.org/xml/rss.xml"
OUTPUT_CSV_PATH = "data/gdacs_alerts.csv"
MAX_RETRIES = 3
RETRY_BACKOFF = 2


def fetch_gdacs_alerts(url=GDACS_RSS_URL, max_retries=MAX_RETRIES):
    """Fetches and parses GDACS disaster alerts from the RSS feed with retry."""
    for attempt in range(1, max_retries + 1):
        try:
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            feed = feedparser.parse(response.content)
            alerts = []
            for entry in feed.entries:
                alert = {
                    "event_type": entry.get("gdacs_eventtype", "Unknown"),
                    "severity": entry.get("gdacs_severity", "Unknown"),
                    "country": entry.get("gdacs_countryname", "Unknown"),
                    "description": entry.get("summary", "No description available"),
                }
                try:
                    alert["date"] = datetime.strptime(
                        entry.get("published", ""),
                        "%a, %d %b %Y %H:%M:%S %Z",
                    ).isoformat()
                except ValueError:
                    alert["date"] = None

                lat = entry.get("geo_lat")
                lon = entry.get("geo_long")
                alert["coordinates"] = f"{lat},{lon}" if lat and lon else None
                alerts.append(alert)

            logger.info(f"Fetched {len(alerts)} alerts from GDACS")
            return alerts

        except requests.exceptions.RequestException as e:
            logger.warning(f"Attempt {attempt}/{max_retries} for GDACS: {e}")
            if attempt < max_retries:
                time.sleep(RETRY_BACKOFF ** attempt)
            else:
                logger.error(f"All {max_retries} attempts failed for GDACS")
                return []
        except Exception as e:
            logger.error(f"Error parsing GDACS feed: {e}")
            return []


def save_alerts_to_csv(alerts, csv_path=OUTPUT_CSV_PATH):
    """Saves alerts to CSV with deduplication against existing file."""
    if not alerts:
        logger.info("No alerts to save.")
        return

    new_df = pd.DataFrame(alerts)
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)

    if os.path.exists(csv_path):
        existing_df = pd.read_csv(csv_path)
        combined = pd.concat([existing_df, new_df], ignore_index=True)
        dedup_cols = ["event_type", "country", "date"]
        available_cols = [c for c in dedup_cols if c in combined.columns]
        if available_cols:
            combined = combined.drop_duplicates(subset=available_cols, keep="last")
        combined.to_csv(csv_path, index=False)
        logger.info(f"Merged alerts into {csv_path} ({len(combined)} total rows)")
    else:
        new_df.to_csv(csv_path, index=False)
        logger.info(f"Saved {len(new_df)} alerts to {csv_path}")


if __name__ == "__main__":
    alerts = fetch_gdacs_alerts()
    if alerts:
        save_alerts_to_csv(alerts)
