import unittest
import src.inequality_analyzer as ia

class TestInequalityAnalyzer(unittest.TestCase):

    def test_gini_coefficient(self):
        income_distribution = [1000, 2000, 3000, 4000, 5000]
        gini = ia.gini_coefficient(income_distribution)
        self.assertAlmostEqual(gini, 0.267, places=2)

        income_distribution = [1000] * 5
        gini = ia.gini_coefficient(income_distribution)
        self.assertAlmostEqual(gini, 0.0, places=3)

        with self.assertRaises(ValueError):
            ia.gini_coefficient([])
        with self.assertRaises(ValueError):
            ia.gini_coefficient([1, -2, 3])

    def test_palma_ratio(self):
        income_distribution = [1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000, 9000, 10000]
        palma = ia.palma_ratio(income_distribution)
        self.assertAlmostEqual(palma, 1.0, places=3)

        income_distribution = [1000] * 10
        palma = ia.palma_ratio(income_distribution)
        self.assertAlmostEqual(palma, 0.25, places=3)

        with self.assertRaises(ValueError):
            ia.palma_ratio([])
        with self.assertRaises(ValueError):
            ia.palma_ratio([1, -2, 3])

    def test_decile_ratios(self):
        income_distribution = [1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000, 9000, 10000]
        decile_ratios_list = ia.decile_ratios(income_distribution)
        self.assertEqual(len(decile_ratios_list), 9)
        self.assertAlmostEqual(decile_ratios_list[0], 10.0, places=3)

        with self.assertRaises(ValueError):
            ia.decile_ratios([])
        with self.assertRaises(ValueError):
            ia.decile_ratios([1, -2, 3])

    def test_inequality_trend_detection(self):
        time_series_data = {2010: 0.4, 2011: 0.42, 2012: 0.44, 2013: 0.46}
        slope, intercept = ia.inequality_trend_detection(time_series_data)
        self.assertAlmostEqual(slope, 0.02, places=5)

        time_series_data = {2010: 0.4}
        trend = ia.inequality_trend_detection(time_series_data)
        self.assertEqual(trend, "No Trend")

        time_series_data = {2010: 0.4, 2011: 0.4}
        slope, intercept = ia.inequality_trend_detection(time_series_data)
        self.assertAlmostEqual(slope, 0.0, places=5)

        with self.assertRaises(ValueError):
            ia.inequality_trend_detection({})

if __name__ == '__main__':
    unittest.main()
