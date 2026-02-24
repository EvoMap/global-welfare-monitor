"""Economic Inequality Analyzer Module."""

import numpy as np
import pandas as pd
from typing import List, Union, Tuple
from scipy.stats import linregress

def gini_coefficient(income_distribution: List[float]) -> float:
    """Calculates the Gini coefficient from income distribution data.

    Args:
        income_distribution: A list of income values representing the income distribution.

    Returns:
        The Gini coefficient, a value between 0 and 1.

    Raises:
        ValueError: If the income distribution is empty or contains non-positive values.
    """
    if not income_distribution:
        raise ValueError("Income distribution cannot be empty.")
    if any(income <= 0 for income in income_distribution):
        raise ValueError("Income values must be positive.")

    income_distribution = np.array(income_distribution)
    n = len(income_distribution)
    index = np.arange(1, n + 1)
    gini = ((np.sum((2 * index - n  - 1) * income_distribution)) / (n * np.sum(income_distribution)))
    return gini


def palma_ratio(income_distribution: List[float]) -> float:
    """Calculates the Palma ratio from income distribution data.

    The Palma ratio is the ratio of the richest 10% of the population's share of gross national income divided
    by the poorest 40%'s share.

    Args:
        income_distribution: A list of income values representing the income distribution.

    Returns:
        The Palma ratio.

    Raises:
        ValueError: If the income distribution is empty or contains non-positive values.
    """
    if not income_distribution:
        raise ValueError("Income distribution cannot be empty.")
    if any(income <= 0 for income in income_distribution):
        raise ValueError("Income values must be positive.")

    income_distribution = sorted(income_distribution)
    n = len(income_distribution)
    top_10_percent = income_distribution[int(0.9 * n):]
    bottom_40_percent = income_distribution[:int(0.4 * n)]

    total_income_top_10 = sum(top_10_percent)
    total_income_bottom_40 = sum(bottom_40_percent)

    if total_income_bottom_40 == 0:
        return float('inf')  # Handle the case where the bottom 40% have zero income

    return total_income_top_10 / total_income_bottom_40


def decile_ratios(income_distribution: List[float]) -> List[float]:
    """Calculates income ratios between deciles.

    Returns a list of ratios, where each element represents the ratio of the income at the top of that decile
    to the income at the bottom of the distribution.

    Args:
        income_distribution: A list of income values representing the income distribution.

    Returns:
        A list of decile ratios.

    Raises:
        ValueError: If the income distribution is empty or contains non-positive values.
    """
    if not income_distribution:
        raise ValueError("Income distribution cannot be empty.")
    if any(income <= 0 for income in income_distribution):
        raise ValueError("Income values must be positive.")

    income_distribution = sorted(income_distribution)
    n = len(income_distribution)
    decile_ratios_list = []
    for i in range(1, 10):
        decile_index = int(i * n / 10)
        decile_ratios_list.append(income_distribution[-1] / income_distribution[0]) # Ratio of richest to poorest
    return decile_ratios_list


def inequality_trend_detection(time_series_data: dict) -> Union[Tuple[float, float], str]:
    """Detects trends in inequality metrics over time using linear regression.

    Args:
        time_series_data: A dictionary where keys are years and values are inequality metric values (e.g., Gini coefficient).

    Returns:
        A tuple containing the slope and intercept of the linear regression, or "No Trend" if the data is insufficient.

    Raises:
        ValueError: If the time series data is empty.
    """
    if not time_series_data:
        raise ValueError("Time series data cannot be empty.")

    years = list(time_series_data.keys())
    inequality_values = list(time_series_data.values())

    if len(years) < 2:
        return "No Trend"  # Not enough data points for trend detection

    slope, intercept, r_value, p_value, std_err = linregress(years, inequality_values)

    return slope, intercept
