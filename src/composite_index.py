import pandas as pd
import numpy as np
from scipy.stats import zscore
import logging
from typing import Dict, List, Optional
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class CompositeIndex:
    """Calculates the Global Welfare Index based on sub-indices."""

    def __init__(self, data: Dict[str, pd.DataFrame], weights: Dict[str, float]) -> None:
        """
        Initializes the CompositeIndex with data and weights.

        Args:
            data (Dict[str, pd.DataFrame]): A dictionary where keys are sub-index names
                and values are pandas DataFrames containing the sub-index data.
                Each DataFrame should have 'country', 'year', and 'value' columns.
            weights (Dict[str, float]): A dictionary where keys are sub-index names and
                values are the weights assigned to each sub-index.
        """
        self.data = data
        self.weights = weights
        self.freshness_scores: Dict[str, float] = {}

    def calculate_freshness_scores(self) -> None:
        """Calculates a freshness score for each sub-index based on the most recent year.
        The score is a linear decay from 1.0 (most recent year) to 0.0 (oldest year).
        """
        current_year = datetime.now().year
        self.freshness_scores = {}
        for index_name, df in self.data.items():
            if not ('year' in df.columns):
                logging.warning(f"'year' column missing in {index_name}, setting freshness to 0")
                self.freshness_scores[index_name] = 0.0
                continue

            max_year = df['year'].max()
            age = current_year - max_year
            # Simple linear decay:  freshness = max(0, 1 - age/10)  (decays to zero over 10 years)
            self.freshness_scores[index_name] = max(0.0, 1.0 - (age / 10.0))
            logging.info(f"Freshness score for {index_name}: {self.freshness_scores[index_name]}")

    def adjust_weights_for_freshness(self) -> None:
        """Adjusts the weights of each sub-index based on its freshness score."""
        self.calculate_freshness_scores()
        for index_name in self.weights:
            if index_name in self.freshness_scores:
                self.weights[index_name] *= self.freshness_scores[index_name]
                logging.info(f"Adjusted weight for {index_name}: {self.weights[index_name]}")
            else:
                logging.warning(f"No freshness score for {index_name}, weight remains unchanged.")

        # Normalize weights to sum to 1 after adjustment
        total_weight = sum(self.weights.values())
        if total_weight > 0:
            for index_name in self.weights:
                self.weights[index_name] /= total_weight
        else:
            logging.warning("Total weight is zero, weights cannot be normalized.")

    def normalize_data(self) -> Dict[str, pd.DataFrame]:
        """Normalizes the data for each sub-index using z-score normalization.

        Returns:
            Dict[str, pd.DataFrame]: A dictionary containing the normalized dataframes.
        """
        normalized_data = {}
        for index_name, df in self.data.items():
            if 'value' not in df.columns:
                logging.error(f"'value' column missing in {index_name}")
                continue
            try:
                df['normalized_value'] = df.groupby('year')['value'].transform(lambda x: zscore(x, nan_policy='omit'))
                normalized_data[index_name] = df
                logging.info(f"Normalized data for {index_name}")
            except Exception as e:
                logging.error(f"Error normalizing data for {index_name}: {e}")

        return normalized_data

    def calculate_composite_index(self) -> pd.DataFrame:
        """Calculates the composite index based on the normalized data and adjusted weights.

        Returns:
            pd.DataFrame: A DataFrame containing the composite index for each country and year.
        """
        self.adjust_weights_for_freshness()
        normalized_data = self.normalize_data()

        # Merge all normalized dataframes into one
        composite_df = None
        for index_name, df in normalized_data.items():
            if composite_df is None:
                composite_df = df[['country', 'year', 'normalized_value']].copy()
                composite_df.rename(columns={'normalized_value': f'{index_name}_normalized'}, inplace=True)
            else:
                composite_df = pd.merge(composite_df, df[['country', 'year', 'normalized_value']],
                                      on=['country', 'year'], how='outer')
                composite_df.rename(columns={'normalized_value': f'{index_name}_normalized'}, inplace=True)

        if composite_df is None:
            logging.warning("No data to calculate composite index.")
            return pd.DataFrame()

        # Calculate data completeness score
        num_indices = len(normalized_data)
        composite_df['data_completeness'] = composite_df.apply(
            lambda row: row.count() / (num_indices + 2), axis=1)  # +2 for country and year

        # Calculate the composite index
        for index_name in self.weights:
            if f'{index_name}_normalized' not in composite_df.columns:
                composite_df[f'{index_name}_normalized'] = 0  # handle missing indices

        composite_df['composite_index'] = 0
        for index_name, weight in self.weights.items():
            composite_df['composite_index'] += composite_df[f'{index_name}_normalized'] * weight

        composite_df.fillna(0, inplace=True)

        return composite_df

    def get_country_ranking(self, year: int) -> pd.DataFrame:
        """Ranks countries based on their composite index for a given year.

        Args:
            year (int): The year for which to rank the countries.

        Returns:
            pd.DataFrame: A DataFrame containing the country rankings for the given year.
        """
        composite_index_df = self.calculate_composite_index()
        year_data = composite_index_df[composite_index_df['year'] == year].copy()
        if year_data.empty:
            logging.warning(f"No data for year {year} to calculate country ranking.")
            return pd.DataFrame()

        year_data['rank'] = year_data['composite_index'].rank(ascending=False)
        year_data.sort_values(by='rank', inplace=True)
        return year_data[['country', 'year', 'composite_index', 'rank']]
