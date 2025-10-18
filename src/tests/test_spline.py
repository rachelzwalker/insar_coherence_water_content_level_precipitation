import unittest
import os
import pandas as pd

from src.GetRollingPrecipitationDataframe import RollingPrecipitationDataframe, WindowTimeframe
from src.Spline import Spline

current_directory = os.getcwd()
path_ground = f'{current_directory}/resources/sample_ground_data'
path_to_save_directory = f'{current_directory}/resources/outputs'
path_insar = f'{current_directory}/resources/InSAR_unzipped_sample'
path_to_points = f'{current_directory}/resources/shape_file_point'

wick_data = pd.read_csv(f'{path_ground}/historical weather data alternative Wick.csv')
wick_data['date'] = pd.to_datetime(wick_data['date'])

one_month_rolling_precipitation = RollingPrecipitationDataframe(wick_data, WindowTimeframe.MONTH, 'prcp',
                                                                'date', 1).get_rolling_mean_dataframe()

six_week_rolling_precipitation = RollingPrecipitationDataframe(wick_data, WindowTimeframe.WEEK, 'prcp',
                                                                'date', 6).get_rolling_mean_dataframe()

class MyTestCase(unittest.TestCase):
    def test_one_month(self):
        precipitation_smoothed_one_month = Spline(one_month_rolling_precipitation, 'Rolling Mean Precipitation',
                                                  'Rolling Mean Precipitation', '1M', 2).get_spline_dataframe()
        self.assertIn('Month', precipitation_smoothed_one_month.columns)  # add assertion here

    def test_one_month_compared_to_six_week(self):
        precipitation_smoothed_one_month = Spline(one_month_rolling_precipitation, 'Rolling Mean Precipitation',
                                                  'Rolling Mean Precipitation', '1M', 2).get_spline_dataframe()
        precipitation_smoothed_six_week = Spline(one_month_rolling_precipitation, 'Rolling Mean Precipitation',
                                                  'Rolling Mean Precipitation', '6W', 2).get_spline_dataframe()
        self.assertGreater(len(precipitation_smoothed_one_month), len(precipitation_smoothed_six_week))

if __name__ == '__main__':
    unittest.main()
