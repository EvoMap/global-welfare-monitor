import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class FoodSecurityMonitor:
    """Monitors food security using IPC data, caloric deficit, and food prices."""

    def __init__(self, alert_thresholds: Dict[str, Dict[str, float]] = None) -> None:
        """Initializes the FoodSecurityMonitor with alert thresholds.

        Args:
            alert_thresholds (Dict[str, Dict[str, float]], optional): A dictionary defining alert thresholds
                for different metrics (e.g., caloric deficit, price volatility).
                Example:
                {
                    "caloric_deficit": {"high": 0.1, "critical": 0.2},
                    "price_volatility": {"high": 0.3, "critical": 0.5}
                }
                Defaults to None.
        """
        self.alert_thresholds = alert_thresholds or {}
        self.logger = logging.getLogger(__name__)
        self.logger.info("FoodSecurityMonitor initialized.")

    def parse_ipc_data(self, ipc_data_path: str) -> pd.DataFrame:
        """Parses IPC (Integrated Food Security Phase Classification) data from a CSV file.

        Args:
            ipc_data_path (str): The path to the IPC data CSV file.

        Returns:
            pd.DataFrame: A DataFrame containing the parsed IPC data.

        Raises:
            FileNotFoundError: If the IPC data file is not found.
            pd.errors.EmptyDataError: If the IPC data file is empty.
            Exception: For other errors during data loading or parsing.
        """
        try:
            self.logger.info(f"Loading IPC data from {ipc_data_path}")
            ipc_data = pd.read_csv(ipc_data_path)
            if ipc_data.empty:
                raise pd.errors.EmptyDataError(f"IPC data file at {ipc_data_path} is empty.")
            self.logger.info(f"IPC data loaded successfully from {ipc_data_path}")
            return ipc_data
        except FileNotFoundError:
            self.logger.error(f"IPC data file not found at {ipc_data_path}")
            raise FileNotFoundError(f"IPC data file not found at {ipc_data_path}")
        except pd.errors.EmptyDataError as e:
            self.logger.error(str(e))
            raise e
        except Exception as e:
            self.logger.exception(f"Error parsing IPC data: {e}")
            raise

    def calculate_caloric_deficit(self, population_data: pd.DataFrame, caloric_needs: float = 2100) -> pd.DataFrame:
        """Calculates the caloric deficit for each region based on population data and caloric needs.

        Args:
            population_data (pd.DataFrame): DataFrame with 'region', 'population', and 'average_calories_consumed' columns.
            caloric_needs (float): The average daily caloric needs per person.

        Returns:
            pd.DataFrame: A DataFrame with 'region' and 'caloric_deficit_percentage' columns.

        Raises:
            ValueError: If the input DataFrame is missing required columns.
        """
        try:
            if not all(col in population_data.columns for col in ['region', 'population', 'average_calories_consumed']):
                raise ValueError(
                    "Population data must contain 'region', 'population', and 'average_calories_consumed' columns."
                )

            population_data['caloric_deficit'] = caloric_needs - population_data['average_calories_consumed']
            population_data['caloric_deficit_percentage'] = (population_data['caloric_deficit'] / caloric_needs) * 100
            self.logger.info("Caloric deficit calculated successfully.")
            return population_data
        except Exception as e:
            self.logger.exception(f"Error calculating caloric deficit: {e}")
            raise

    def calculate_food_price_volatility(self, price_data: pd.DataFrame, window_size: int = 3) -> pd.DataFrame:
        """Calculates the food price volatility for each region.

        Args:
            price_data (pd.DataFrame): DataFrame with 'region', 'date', and 'price' columns.
            window_size (int): The rolling window size for calculating volatility.

        Returns:
            pd.DataFrame: A DataFrame with 'region' and 'price_volatility' columns.

        Raises:
            ValueError: If the input DataFrame is missing required columns.
        """
        try:
            if not all(col in price_data.columns for col in ['region', 'date', 'price']):
                raise ValueError("Price data must contain 'region', 'date', and 'price' columns.")

            # Sort by region and date
            price_data = price_data.sort_values(by=['region', 'date'])

            def calculate_volatility(series):
                return series.std() / series.mean() if series.mean() != 0 else 0

            price_data['price_volatility'] = price_data.groupby('region')['price'].rolling(window=window_size).apply(calculate_volatility).reset_index(drop=True)

            price_data = price_data.dropna(subset=['price_volatility'])

            self.logger.info("Food price volatility calculated successfully.")
            return price_data
        except Exception as e:
            self.logger.exception(f"Error calculating food price volatility: {e}")
            raise

    def assess_alerts(self, caloric_deficit_data: pd.DataFrame, price_volatility_data: pd.DataFrame) -> Dict[str, List[str]]:
        """Assesses alerts based on caloric deficit and price volatility data.

        Args:
            caloric_deficit_data (pd.DataFrame): DataFrame with 'region' and 'caloric_deficit_percentage' columns.
            price_volatility_data (pd.DataFrame): DataFrame with 'region' and 'price_volatility' columns.

        Returns:
            Dict[str, List[str]]: A dictionary of alerts, with severity levels as keys and lists of regions as values.
        """
        alerts = {
            "high": [],
            "critical": []
        }

        if not self.alert_thresholds:
            self.logger.warning("Alert thresholds not configured. No alerts will be generated.")
            return alerts

        # Caloric Deficit Alerts
        if 'caloric_deficit' in self.alert_thresholds:
            high_threshold = self.alert_thresholds['caloric_deficit'].get('high', float('inf'))
            critical_threshold = self.alert_thresholds['caloric_deficit'].get('critical', float('inf'))

            for index, row in caloric_deficit_data.iterrows():
                region = row['region']
                deficit = row['caloric_deficit_percentage']

                if deficit >= critical_threshold:
                    alerts['critical'].append(region)
                elif deficit >= high_threshold:
                    alerts['high'].append(region)

        # Price Volatility Alerts
        if 'price_volatility' in self.alert_thresholds:
            high_threshold = self.alert_thresholds['price_volatility'].get('high', float('inf'))
            critical_threshold = self.alert_thresholds['price_volatility'].get('critical', float('inf'))

            for index, row in price_volatility_data.iterrows():
                region = row['region']
                volatility = row['price_volatility']

                if volatility >= critical_threshold:
                    alerts['critical'].append(region)
                elif volatility >= high_threshold:
                    alerts['high'].append(region)

        self.logger.info(f"Alerts assessed: {alerts}")
        return alerts
