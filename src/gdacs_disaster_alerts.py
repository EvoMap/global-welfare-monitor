"""
Fetches real-time disaster alerts from the Global Disaster Alert and Coordination System (GDACS) API/RSS feed.
Parses earthquake, flood, cyclone, and drought events.
Standardizes output with columns: event_type, severity, country, date, coordinates, description.
Saves to data/gdacs_alerts.csv.
"""
import feedparser
import pandas as pd
import requests
from datetime import datetime
import os

GDACS_RSS_URL = "https://www.gdacs.org/xml/rss.xml"
OUTPUT_CSV_PATH = "data/gdacs_alerts.csv"

def fetch_gdacs_alerts(url=GDACS_RSS_URL):
    """Fetches and parses GDACS disaster alerts from the RSS feed.

    Args:
        url (str): The URL of the GDACS RSS feed.

    Returns:
        list: A list of dictionaries, where each dictionary represents a disaster alert.
               Returns an empty list if an error occurs.
    """
    try:
        response = requests.get(url, timeout=10)  # Added timeout
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        feed = feedparser.parse(response.content)
        alerts = []
        for entry in feed.entries:
            alert = {}
            alert['event_type'] = entry.get('gdacs_eventtype', 'Unknown')
            alert['severity'] = entry.get('gdacs_severity', 'Unknown')
            alert['country'] = entry.get('gdacs_countryname', 'Unknown')

            # Handle date parsing errors
            try:
                alert['date'] = datetime.strptime(entry.get('published', ''), '%a, %d %b %Y %H:%M:%S %Z').isoformat()
            except ValueError:
                alert['date'] = None  # Or a default date, e.g., datetime.now().isoformat()

            alert['coordinates'] = entry.get('geo_lat', None), entry.get('geo_long', None)
            alert['description'] = entry.get('summary', 'No description available')
            alerts.append(alert)
        return alerts
    except requests.exceptions.RequestException as e:
        print(f"Error fetching GDACS feed: {e}")
        return []
    except Exception as e:
        print(f"Error parsing GDACS feed: {e}")
        return []


def save_alerts_to_csv(alerts, csv_path=OUTPUT_CSV_PATH):
    """Saves the disaster alerts to a CSV file.

    Args:
        alerts (list): A list of disaster alert dictionaries.
        csv_path (str): The path to the CSV file to save.
    """
    if not alerts:
        print("No alerts to save.")
        return

    df = pd.DataFrame(alerts)

    # Ensure the 'data' directory exists
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)

    df.to_csv(csv_path, index=False)
    print(f"Saved alerts to {csv_path}")



if __name__ == "__main__":
    alerts = fetch_gdacs_alerts()
    if alerts:
        save_alerts_to_csv(alerts)
