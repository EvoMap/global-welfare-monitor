"""Streamlit dashboard for the Global Welfare Monitor."""

import streamlit as st
import os

DATA_DIR = os.environ.get("DATA_DIR", "/data")

st.title("Global Welfare Monitor Dashboard")

# Example: Display data from the dummy data file
filepath = os.path.join(DATA_DIR, "dummy_data.txt")

try:
    with open(filepath, "r") as f:
        data = f.read()
    st.write("Data:")
    st.write(data)
except FileNotFoundError:
    st.write("No data available yet. Please run the data ingestion pipeline.")
