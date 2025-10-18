import unittest
import pandas as pd
import numpy as np

from src.GetSummaryMetrics import GetSummaryMetrics


# Generate three DataFrames outside the test class
def create_random_df():
    """Creates a DataFrame with 'Date' and 'mean' columns"""
    dates = pd.date_range(start="2024-01-01", periods=10)
    df = pd.DataFrame({
        "Date": dates,
        "mean": np.random.rand(10)  # Random float values between 0-1
    })
    return df

df1 = create_random_df()
df2 = create_random_df()
df3 = create_random_df()

dataframes = {'1': df1, '2': df2, '3': df3}

class MyTestCase(unittest.TestCase):
    def test_output_dataframe_has_expected_metric_column(self):
        summary_dataframe = GetSummaryMetrics(dataframes).run()
        self.assertIn('Maximum Coherence', summary_dataframe.columns)

    def test_output_dataframe_has_site_column(self):
        summary_dataframe = GetSummaryMetrics(dataframes).run()
        self.assertIn('Site', summary_dataframe.columns)

    def test_length_summary_dataframe(self):
        summary_dataframe = GetSummaryMetrics(dataframes).run()
        self.assertEqual(len(summary_dataframe), 3)


if __name__ == '__main__':
    unittest.main()
