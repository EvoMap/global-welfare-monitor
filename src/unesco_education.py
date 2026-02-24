"""Module for fetching and processing education access metrics from the UNESCO Institute for Statistics (UIS) API.

This module retrieves enrollment rates, literacy rates, and out-of-school children counts by country,
parses the data into a standardized DataFrame, performs data quality validation, and saves the data to a CSV file.

It uses the pandas and requests libraries for data manipulation and API interaction, respectively.
"""

import pandas as pd
import requests
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class UNESCOEducationData:
    """A class to fetch, process, and save UNESCO education data."""

    def __init__(self, api_url='http://api.uis.unesco.org/'):
        """Initializes the UNESCOEducationData object.

        Args:
            api_url (str): The base URL of the UNESCO API.
        """
        self.api_url = api_url
        self.data = None

    def fetch_data(self, endpoint, params=None):
        """Fetches data from the UNESCO API endpoint.

        Args:
            endpoint (str): The API endpoint to fetch data from.
            params (dict, optional): Query parameters for the API request. Defaults to None.

        Returns:
            list: A list of dictionaries containing the data, or None if an error occurs.
        """
        try:
            response = requests.get(f'{self.api_url}{endpoint}', params=params)
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
            return response.json()
        except requests.exceptions.RequestException as e:
            logging.error(f'Error fetching data from UNESCO API: {e}')
            return None

    def get_education_data(self):
        """Retrieves education data from the UNESCO API.

        This method fetches enrollment rates, literacy rates, and out-of-school children counts by country.

        Returns:
            pandas.DataFrame: A DataFrame containing the processed education data, or None if an error occurs.
        """
        # Example indicators (replace with actual UNESCO indicator codes)
        indicators = {
            'UIS.NERA.1': 'Enrollment Rate, Primary',  # Example: Net Enrollment Rate, Primary
            'UIS.LIT.A': 'Literacy Rate, Adult',  # Example: Adult Literacy Rate
            'UIS.OOSC.1': 'Out-of-School Children, Primary'  # Example: Out-of-School Children, Primary
        }

        all_data = []
        for indicator_code, indicator_name in indicators.items():
            data = self.fetch_data('data', params={'indicator': indicator_code, 'format': 'json'}) # Adjust endpoint as needed
            if data:
                for item in data:
                    try:
                        country = item.get('country')
                        year = item.get('year')
                        value = item.get('value')

                        if country and year and value is not None:
                            all_data.append({
                                'Country': country,
                                'Year': year,
                                'Indicator': indicator_name,
                                'Value': value
                            })
                    except (TypeError, ValueError) as e:
                        logging.warning(f'Skipping invalid data point: {item}. Error: {e}')
            else:
                logging.warning(f'No data received for indicator: {indicator_code}')

        if not all_data:
            logging.warning('No education data retrieved from UNESCO API.')
            return None

        df = pd.DataFrame(all_data)
        self.data = df
        return df

    def validate_data(self, df):
        """Validates the data for missing values and data types.

        Args:
            df (pandas.DataFrame): The DataFrame to validate.

        Returns:
            bool: True if the data is valid, False otherwise.
        """
        if df.isnull().sum().sum() > 0:
            logging.error('Data contains missing values.')
            return False

        # Check data types (example: Value should be numeric)
        if not pd.api.types.is_numeric_dtype(df['Value']):
            logging.error('Value column is not numeric.')
            return False

        return True

    def save_data(self, df, filepath='data/unesco_education.csv'):
        """Saves the DataFrame to a CSV file.

        Args:
            df (pandas.DataFrame): The DataFrame to save.
            filepath (str): The path to the CSV file.
        """
        try:
            df.to_csv(filepath, index=False)
            logging.info(f'UNESCO education data saved to {filepath}')
        except Exception as e:
            logging.error(f'Error saving data to CSV: {e}')

def main():
    """Main function to execute the data fetching, processing, and saving.

    This function creates an instance of UNESCOEducationData, retrieves the education data,
    validates the data, and saves it to a CSV file.
    """
    education_data = UNESCOEducationData()
    df = education_data.get_education_data()

    if df is not None:
        if education_data.validate_data(df):
            education_data.save_data(df)
        else:
            logging.error('Data validation failed. Data not saved.')
    else:
        logging.error('Failed to retrieve education data.')

if __name__ == "__main__":
    main()