# Data Sources

This document lists the data sources used by the Global Welfare Monitor, along with their APIs, update frequency, and data schemas.

## World Health Organization (WHO)

*   **API:** WHO API (Specific endpoints vary depending on the data being accessed.  Requires registration and API key.)
*   **Update Frequency:** Varies depending on the indicator (typically monthly or quarterly).
*   **Data Schema:**
    
    {
      "indicator": "string",
      "country": "string",
      "year": "integer",
      "value": "number",
      "unit": "string"
    }
    

## Food and Agriculture Organization (FAO)

*   **API:** FAOSTAT API (Requires registration and API key.)
*   **Update Frequency:** Annually
*   **Data Schema:**
    
    {
      "item": "string",
      "country": "string",
      "year": "integer",
      "element": "string",
      "value": "number",
      "unit": "string"
    }
    

## Global Disaster Alert and Coordination System (GDACS)

*   **API:** GDACS API (Open API, no registration required.)
*   **Update Frequency:** Real-time
*   **Data Schema:**
    
    {
      "eventid": "string",
      "name": "string",
      "latitude": "number",
      "longitude": "number",
      "severity": "string",
      "populationAffected": "integer",
      "vulnerability": "string",
      "date": "string"
    }
    

## Example: Adding a new Data Source

To add a new data source, follow these steps:

1.  Implement the data ingestion logic in the `src/data_ingestion.py` module.
2.  Add a new entry to this `docs/DATA_SOURCES.md` file with the following information:
    *   **Data Source Name:** The name of the data source.
    *   **API:** The API endpoint for the data source.
    *   **Update Frequency:** How often the data is updated.
    *   **Data Schema:** A JSON schema describing the structure of the data.

**Important:** Ensure that you handle API rate limits and errors gracefully.
