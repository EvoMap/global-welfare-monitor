"""Data ingestion script for the Global Welfare Monitor."""

import os
import time

DATA_DIR = os.environ.get("DATA_DIR", "/data")


def ingest_data():
    """Simulates data ingestion from various sources."""
    print("Starting data ingestion...")

    os.makedirs(DATA_DIR, exist_ok=True)

    time.sleep(5)
    print("Data ingestion complete.")

    filepath = os.path.join(DATA_DIR, "dummy_data.txt")
    with open(filepath, "w") as f:
        f.write("This is dummy data.")
    print(f"Dummy data written to {filepath}")

if __name__ == "__main__":
    ingest_data()
