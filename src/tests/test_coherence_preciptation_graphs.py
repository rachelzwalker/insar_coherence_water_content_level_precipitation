import unittest
import os
import pandas as pd

from src.GeoDataFrameLocationCoherence import GeoDataframeLocationCoherence
from src.GetCoherenceGraphsDataDictionary import GetCoherenceGraphsDataDictionary
from src.GetRollingPrecipitationDataframe import RollingPrecipitationDataframe, WindowTimeframe
from src.MovingWindow import MovingWindow, GetRollingMean
from src.CoherencePrecipitationGraphs import CoherencePrecipitationGraphs

current_directory = os.getcwd()
path_ground = f'{current_directory}/resources/sample_ground_data'
path_to_save_directory = f'{current_directory}/resources/outputs'
path_insar = f'{current_directory}/resources/InSAR_unzipped_sample'
path_to_points = f'{current_directory}/resources/shape_file_point'

munsary_ef_weather = pd.read_csv(f'{path_ground}/MUN_ENV_SITEEF.csv')
munsary_ef_weather['Date'] = pd.to_datetime(munsary_ef_weather['Date'])

one_month_rolling_precipitation = RollingPrecipitationDataframe(munsary_ef_weather, WindowTimeframe.MONTH,
                                                                name_of_date_column='Date').get_rolling_mean_dataframe()

data_dictionary = GetCoherenceGraphsDataDictionary(path_insar, path_ground, path_to_points,
                                                   path_to_save_directory=path_to_save_directory, location='Munsary EF',
                                                   site='MUN', subsite='EF', input_data='point').run_method()
munsary_ef_dataframe = data_dictionary['coherence_ground_dataframe']
dataframe = GeoDataframeLocationCoherence(path_insar, location='Munsary EF',
                                          path_to_points=path_to_points,
                                          input_data='point',
                                          data_series_dates_to_remove=None).dataframe_coherence()
rolling_means_dataframes = GetRollingMean(None).rolling_means_with_window(dataframe)
rolling_means_one_month = rolling_means_dataframes['one_month_rolling_mean_coherence'].rename_axis('time')
rolling_means_one_month = rolling_means_one_month.sort_values(by='Date')



class MyTestCase(unittest.TestCase):
    def test_something(self):
        CoherencePrecipitationGraphs(rolling_means_one_month, one_month_rolling_precipitation, path_to_save_directory,
                                     'Munsary EF',
                                     '1_month')._rolling_mean_graph()

        self.assertTrue(f'{path_to_save_directory}/overall_coherence_precipitation_Munsary EF_1_month.png')  # add assertion here


if __name__ == '__main__':
    unittest.main()
