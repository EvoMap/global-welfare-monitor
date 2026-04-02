import pytest
import pandas as pd
from src.composite_index import CompositeIndex
import numpy as np

@pytest.fixture
def sample_data():
    """Provides sample data for testing."""
    data = {
        'health': pd.DataFrame({
            'country': ['USA', 'USA', 'CAN', 'CAN'],
            'year': [2020, 2021, 2020, 2021],
            'value': [78, 79, 82, 83]
        }),
        'economy': pd.DataFrame({
            'country': ['USA', 'USA', 'CAN', 'CAN'],
            'year': [2020, 2021, 2020, 2021],
            'value': [60000, 62000, 50000, 52000]
        }),
        'education': pd.DataFrame({
            'country': ['USA', 'USA', 'CAN', 'CAN'],
            'year': [2020, 2021, 2020, 2021],
            'value': [14, 15, 16, 17]
        })
    }
    return data

@pytest.fixture
def sample_weights():
    """Provides sample weights for testing."""
    weights = {
        'health': 0.4,
        'economy': 0.3,
        'education': 0.3
    }
    return weights

def test_composite_index_initialization(sample_data, sample_weights):
    """Tests the initialization of the CompositeIndex class."""
    composite_index = CompositeIndex(sample_data, sample_weights)
    assert composite_index.data == sample_data
    assert composite_index.weights == sample_weights

def test_calculate_freshness_scores(sample_data, sample_weights):
    """Tests the calculate_freshness_scores method."""
    composite_index = CompositeIndex(sample_data, sample_weights)
    composite_index.calculate_freshness_scores()
    assert all(0 <= score <= 1 for score in composite_index.freshness_scores.values())

def test_adjust_weights_for_freshness(sample_data, sample_weights):
    """Tests the adjust_weights_for_freshness method."""
    composite_index = CompositeIndex(sample_data, sample_weights)
    composite_index.adjust_weights_for_freshness()
    assert sum(composite_index.weights.values()) == pytest.approx(1.0)
    assert all(v >= 0 for v in composite_index.weights.values())

def test_normalize_data(sample_data, sample_weights):
    """Tests the normalize_data method."""
    composite_index = CompositeIndex(sample_data, sample_weights)
    normalized_data = composite_index.normalize_data()
    for index_name, df in normalized_data.items():
        assert 'normalized_value' in df.columns
        for year in df['year'].unique():
            year_data = df[df['year'] == year]['normalized_value']
            if len(year_data) > 1:
                assert np.isclose(year_data.mean(), 0, atol=1e-6)

def test_calculate_composite_index(sample_data, sample_weights):
    """Tests the calculate_composite_index method."""
    composite_index = CompositeIndex(sample_data, sample_weights)
    composite_index_df = composite_index.calculate_composite_index()
    assert not composite_index_df.empty
    assert 'country' in composite_index_df.columns
    assert 'composite_index' in composite_index_df.columns

def test_get_country_ranking(sample_data, sample_weights):
    """Tests the get_country_ranking method."""
    composite_index = CompositeIndex(sample_data, sample_weights)
    ranking_df = composite_index.get_country_ranking(2020)
    if not ranking_df.empty:
        assert 'country' in ranking_df.columns
        assert 'composite_index' in ranking_df.columns
        assert 'rank' in ranking_df.columns
