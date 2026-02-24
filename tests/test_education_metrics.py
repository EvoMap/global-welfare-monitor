import unittest
import pandas as pd
from src.education_metrics import (
    normalize_literacy_rate,
    calculate_enrollment_ratio,
    compute_gender_parity_index,
    calculate_spending_efficiency,
)


class TestEducationMetrics(unittest.TestCase):

    def setUp(self):
        self.data = pd.DataFrame({
            'region': ['A', 'A', 'B', 'B'],
            'age_group': ['5-10', '11-15', '5-10', '11-15'],
            'literacy_rate': [0.6, 0.8, 0.7, 0.9],
            'population': [1000, 1200, 800, 900],
            'enrolled': [600, 960, 560, 810],
            'male_enrollment': [300, 480, 280, 405],
            'female_enrollment': [300, 480, 280, 405],
            'education_expenditure': [10000, 12000, 8000, 9000],
            'test_scores': [60, 70, 55, 65]
        })

    def test_normalize_literacy_rate(self):
        result = normalize_literacy_rate(self.data.copy(), 'age_group', 'region', 'literacy_rate')
        self.assertIn('normalized_literacy_rate', result.columns)
        self.assertTrue(all(0 <= val <= 1 for val in result['normalized_literacy_rate']))

        # Test with missing column
        data_missing_col = self.data.drop('literacy_rate', axis=1)
        result_missing_col = normalize_literacy_rate(data_missing_col.copy(), 'age_group', 'region', 'literacy_rate')
        self.assertNotIn('normalized_literacy_rate', result_missing_col.columns)

    def test_calculate_enrollment_ratio(self):
        result = calculate_enrollment_ratio(self.data.copy(), 'population', 'enrolled')
        self.assertIn('enrollment_ratio', result.columns)
        self.assertTrue(all(0 <= val <= 1 for val in result['enrollment_ratio']))

        # Test with zero population
        data_zero_pop = self.data.copy()
        data_zero_pop.loc[0, 'population'] = 0
        result_zero_pop = calculate_enrollment_ratio(data_zero_pop, 'population', 'enrolled')
        self.assertEqual(result_zero_pop['enrollment_ratio'][0], 0)

    def test_compute_gender_parity_index(self):
        result = compute_gender_parity_index(self.data.copy(), 'male_enrollment', 'female_enrollment')
        self.assertIn('gender_parity_index', result.columns)
        self.assertTrue(all(val >= 0 for val in result['gender_parity_index']))

        # Test with zero male enrollment
        data_zero_male = self.data.copy()
        data_zero_male.loc[0, 'male_enrollment'] = 0
        result_zero_male = compute_gender_parity_index(data_zero_male, 'male_enrollment', 'female_enrollment')
        self.assertEqual(result_zero_male['gender_parity_index'][0], 0)

    def test_calculate_spending_efficiency(self):
        result = calculate_spending_efficiency(self.data.copy(), 'education_expenditure', 'test_scores')
        self.assertIn('spending_efficiency', result.columns)
        self.assertTrue(all(val >= 0 for val in result['spending_efficiency']))

        # Test with zero expenditure
        data_zero_exp = self.data.copy()
        data_zero_exp.loc[0, 'education_expenditure'] = 0
        result_zero_exp = calculate_spending_efficiency(data_zero_exp, 'education_expenditure', 'test_scores')
        self.assertEqual(result_zero_exp['spending_efficiency'][0], 0)


if __name__ == '__main__':
    unittest.main()
