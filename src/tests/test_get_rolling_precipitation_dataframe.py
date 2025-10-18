import unittest
import os
import pandas as pd

from src.GetRollingPrecipitationDataframe import RollingPrecipitationDataframe, WindowTimeframe

current_directory = os.getcwd()
path_ground = f'{current_directory}/resources/sample_ground_data'
wick_data = pd.read_csv(f'{path_ground}/historical weather data alternative Wick.csv')

wick_data['date'] = pd.to_datetime(wick_data['date'])

munsary_ef_weather = pd.read_csv(f'{path_ground}/MUN_ENV_SITEEF.csv')
munsary_ef_weather['Date'] = pd.to_datetime(munsary_ef_weather['Date'])


class MyTestCase(unittest.TestCase):
    def test_add_rolling_mean_column(self):
        rolling_dataframe = RollingPrecipitationDataframe(wick_data, WindowTimeframe.MONTH).get_rolling_mean_dataframe()
        self.assertIn('Rolling Mean Precipitation', rolling_dataframe.columns)

    def test_check_size_of_dataframe_reduced(self):
        rolling_dataframe = RollingPrecipitationDataframe(wick_data, WindowTimeframe.MONTH).get_rolling_mean_dataframe()
        self.assertLess(len(rolling_dataframe), len(wick_data))

    def test_check_sizes_of_month_week_dataframes(self):
        rolling_dataframe_month = RollingPrecipitationDataframe(wick_data,
                                                                WindowTimeframe.MONTH).get_rolling_mean_dataframe()
        rolling_dataframe_week = RollingPrecipitationDataframe(wick_data, WindowTimeframe.WEEK,
                                                               number=6).get_rolling_mean_dataframe()
        self.assertLess(len(rolling_dataframe_week), len(rolling_dataframe_month))

    def test_check_size_of_dataframe_reduced_munsary(self):
        rolling_dataframe = RollingPrecipitationDataframe(munsary_ef_weather, WindowTimeframe.MONTH,
                                                          name_of_date_column='Date').get_rolling_mean_dataframe()
        self.assertLess(len(rolling_dataframe), len(munsary_ef_weather))


if __name__ == '__main__':
    unittest.main()
