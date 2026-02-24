import pytest
import pandas as pd
from src import data_processing


def test_merge_dataframes(mock_who_data, mock_world_bank_data, expected_processed_data):
    """Test merging of WHO and World Bank dataframes."""
    who_df = data_processing.transform_who_data(mock_who_data)
    world_bank_df = data_processing.transform_world_bank_data(mock_world_bank_data)
    merged_df = data_processing.merge_dataframes(who_df, world_bank_df)

    pd.testing.assert_frame_equal(merged_df.sort_values(by=['country', 'year']).reset_index(drop=True), expected_processed_data.sort_values(by=['country', 'year']).reset_index(drop=True))


def test_merge_dataframes_empty_who(mock_world_bank_data):
    """Test merging with an empty WHO dataframe."""
    world_bank_df = data_processing.transform_world_bank_data(mock_world_bank_data)
    merged_df = data_processing.merge_dataframes(pd.DataFrame(), world_bank_df)
    assert merged_df.empty


def test_merge_dataframes_empty_world_bank(mock_who_data):
    """Test merging with an empty World Bank dataframe."""
    who_df = data_processing.transform_who_data(mock_who_data)
    merged_df = data_processing.merge_dataframes(who_df, pd.DataFrame())
    assert merged_df.empty


def test_merge_dataframes_no_common_columns():
    """Test merging dataframes with no common columns."""
    df1 = pd.DataFrame({'col1': [1, 2], 'col2': [3, 4]})
    df2 = pd.DataFrame({'col3': [5, 6], 'col4': [7, 8]})
    merged_df = data_processing.merge_dataframes(df1, df2)
    assert merged_df.empty


def test_transform_who_data(mock_who_data):
    """Test the transform_who_data function from data_processing."""
    df = data_processing.transform_who_data(mock_who_data)
    assert isinstance(df, pd.DataFrame)
    assert 'country' in df.columns
    assert 'year' in df.columns
    assert 'life_expectancy' in df.columns


def test_transform_world_bank_data(mock_world_bank_data):
    """Test the transform_world_bank_data function from data_processing."""
    df = data_processing.transform_world_bank_data(mock_world_bank_data)
    assert isinstance(df, pd.DataFrame)
    assert 'country' in df.columns
    assert 'year' in df.columns
    assert 'gdp_per_capita' in df.columns