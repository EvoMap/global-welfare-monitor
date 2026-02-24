import pandas as pd
import numpy as np
from scipy import stats
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def normalize_metric(data: pd.Series) -> pd.Series:
    """Normalizes a healthcare metric to a range of 0-1.

    Args:
        data (pd.Series): A pandas Series containing the metric values.

    Returns:
        pd.Series: A pandas Series containing the normalized metric values.
    """
    try:
        min_val = data.min()
        max_val = data.max()
        if min_val == max_val:
            logging.warning("Normalization failed: min and max values are equal.")
            return pd.Series(np.zeros(len(data)))
        normalized_data = (data - min_val) / (max_val - min_val)
        return normalized_data
    except Exception as e:
        logging.error(f"Error during normalization: {e}")
        return pd.Series(np.zeros(len(data)))


def compute_composite_index(data: pd.DataFrame, weights: dict) -> pd.Series:
    """Computes a weighted composite index for healthcare access.

    Args:
        data (pd.DataFrame): A pandas DataFrame containing normalized healthcare metrics.
        weights (dict): A dictionary specifying the weights for each metric.

    Returns:
        pd.Series: A pandas Series containing the composite index scores.
    """
    try:
        composite_index = pd.Series(np.zeros(len(data)), index=data.index)
        for metric, weight in weights.items():
            if metric not in data.columns:
                raise ValueError(f"Metric '{metric}' not found in the data.")
            composite_index += data[metric] * weight
        return composite_index
    except ValueError as ve:
        logging.error(f"ValueError during composite index computation: {ve}")
        return pd.Series(np.zeros(len(data)), index=data.index)
    except Exception as e:
        logging.error(f"Error during composite index computation: {e}")
        return pd.Series(np.zeros(len(data)), index=data.index)


def rank_countries(index_scores: pd.Series, confidence_interval: float = 0.95) -> pd.DataFrame:
    """Ranks countries by healthcare access index and provides confidence intervals.

    Args:
        index_scores (pd.Series): A pandas Series containing the composite index scores.
        confidence_interval (float): The desired confidence interval (default: 0.95).

    Returns:
        pd.DataFrame: A pandas DataFrame containing the ranked countries, index scores,
                      mean, standard error, and confidence interval bounds.
    """
    try:
        ranked_countries = index_scores.sort_values(ascending=False).to_frame(name='index_score')
        mean = index_scores.mean()
        std_err = stats.sem(index_scores)
        interval = std_err * stats.t.ppf((1 + confidence_interval) / 2, len(index_scores) - 1)
        ranked_countries['mean'] = mean
        ranked_countries['standard_error'] = std_err
        ranked_countries['confidence_interval_lower'] = mean - interval
        ranked_countries['confidence_interval_upper'] = mean + interval
        return ranked_countries
    except Exception as e:
        logging.error(f"Error during country ranking: {e}")
        return pd.DataFrame()


def identify_outliers(index_scores: pd.Series, threshold: float = 3.0) -> pd.Series:
    """Identifies statistical outliers in the healthcare access index.

    Args:
        index_scores (pd.Series): A pandas Series containing the composite index scores.
        threshold (float): The Z-score threshold for identifying outliers (default: 3.0).

    Returns:
        pd.Series: A pandas Series containing the identified outliers.
    """
    try:
        z_scores = np.abs(stats.zscore(index_scores))
        outliers = index_scores[z_scores > threshold]
        return outliers
    except Exception as e:
        logging.error(f"Error during outlier identification: {e}")
        return pd.Series()
