import pytest
import pandas as pd
import numpy as np
from src import healthcare_index
import logging

# Suppress logging during tests
logging.disable(logging.CRITICAL)


@pytest.fixture
def sample_data():
    """Fixture to provide sample healthcare data."""
    data = {
        'country': ['USA', 'Canada', 'Mexico'],
        'life_expectancy': [78.0, 82.0, 75.0],
        'access_to_healthcare': [0.9, 0.95, 0.8],
        'infant_mortality': [5.0, 4.0, 6.0]
    }
    return pd.DataFrame(data)


def test_normalize_metric(sample_data):
    """Test the normalize_metric function."""
    life_expectancy = sample_data['life_expectancy']
    normalized_life_expectancy = healthcare_index.normalize_metric(life_expectancy)
    assert isinstance(normalized_life_expectancy, pd.Series)
    assert normalized_life_expectancy.min() == 0.0
    assert normalized_life_expectancy.max() == 1.0


def test_normalize_metric_edge_case_same_values():
    """Test normalize_metric with all values the same."""
    data = pd.Series([5, 5, 5, 5])
    normalized_data = healthcare_index.normalize_metric(data)
    assert all(normalized_data == 0.0)


def test_compute_composite_index(sample_data):
    """Test the compute_composite_index function."""
    # Normalize the data
    normalized_data = sample_data[['life_expectancy', 'access_to_healthcare', 'infant_mortality']].copy()
    for col in normalized_data.columns:
        normalized_data[col] = healthcare_index.normalize_metric(sample_data[col])

    weights = {'life_expectancy': 0.4, 'access_to_healthcare': 0.4, 'infant_mortality': 0.2}
    composite_index = healthcare_index.compute_composite_index(normalized_data, weights)
    assert isinstance(composite_index, pd.Series)
    assert len(composite_index) == len(sample_data)


def test_compute_composite_index_missing_metric(sample_data):
    """Test compute_composite_index with a missing metric."""
    normalized_data = sample_data[['life_expectancy', 'access_to_healthcare']].copy()
    for col in normalized_data.columns:
        normalized_data[col] = healthcare_index.normalize_metric(sample_data[col])
    weights = {'life_expectancy': 0.5, 'access_to_healthcare': 0.5, 'missing_metric': 0.2}
    with pytest.raises(ValueError):
        healthcare_index.compute_composite_index(normalized_data, weights)


def test_rank_countries(sample_data):
    """Test the rank_countries function."""
    # Normalize the data
    normalized_data = sample_data[['life_expectancy', 'access_to_healthcare', 'infant_mortality']].copy()
    for col in normalized_data.columns:
        normalized_data[col] = healthcare_index.normalize_metric(sample_data[col])

    weights = {'life_expectancy': 0.4, 'access_to_healthcare': 0.4, 'infant_mortality': 0.2}
    composite_index = healthcare_index.compute_composite_index(normalized_data, weights)
    ranked_countries = healthcare_index.rank_countries(composite_index)
    assert isinstance(ranked_countries, pd.DataFrame)
    assert 'index_score' in ranked_countries.columns
    assert 'mean' in ranked_countries.columns
    assert 'standard_error' in ranked_countries.columns
    assert 'confidence_interval_lower' in ranked_countries.columns
    assert 'confidence_interval_upper' in ranked_countries.columns


def test_rank_countries_empty_index():
    """Test rank_countries with an empty index."""
    index_scores = pd.Series([])
    ranked_countries = healthcare_index.rank_countries(index_scores)
    assert isinstance(ranked_countries, pd.DataFrame)


def test_identify_outliers(sample_data):
    """Test the identify_outliers function."""
    # Normalize the data
    normalized_data = sample_data[['life_expectancy', 'access_to_healthcare', 'infant_mortality']].copy()
    for col in normalized_data.columns:
        normalized_data[col] = healthcare_index.normalize_metric(sample_data[col])

    weights = {'life_expectancy': 0.4, 'access_to_healthcare': 0.4, 'infant_mortality': 0.2}
    composite_index = healthcare_index.compute_composite_index(normalized_data, weights)
    outliers = healthcare_index.identify_outliers(composite_index)
    assert isinstance(outliers, pd.Series)
