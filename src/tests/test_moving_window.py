import unittest
import os
from src.GeoDataFrameLocationCoherence import GeoDataframeLocationCoherence
from src.GetCoherenceGraphsDataDictionary import GetCoherenceGraphsDataDictionary
from src.GetDFGroundData import GetDFGroundData
from src.MovingWindow import GetRollingMean, MovingWindow, Variable

current_directory = os.getcwd()
path = f'{current_directory}/resources/InSAR_unzipped_sample'
path_to_points = f'{current_directory}/resources/shape_file_point'

current_directory = os.getcwd()
path_ground = f'{current_directory}/resources/sample_ground_data'
path_insar = f'{current_directory}/resources/InSAR_unzipped_sample'
reference_date = '2018-04-02'
location = 'Munsary EF'
input_data = 'point'
output_path = f'{current_directory}/resources/outputs'


munsary_ef_ppt = GetDFGroundData(data_path=path_ground, data_type='ab', site='MUN', subsite='EF',
                                 variable='prcp').get_variable_and_date_specific_csv()
munsary_ef_ppt = munsary_ef_ppt.rename(columns={'prcp': 'Precipitation_mm'})

class MyTestCase(unittest.TestCase):
    def test_rolling_mean(self):
        coherence_dataframe = GeoDataframeLocationCoherence(path, location='Munsary EF',
                                                            path_to_points=path_to_points,
                                                            input_data='point',
                                                            data_series_dates_to_remove=None).dataframe_coherence()
        rolling_means_dataframes = GetRollingMean(None).rolling_means_with_window(coherence_dataframe)
        rolling_means_one_month = rolling_means_dataframes['one_month_rolling_mean_coherence'].rename_axis('time')
        self.assertIn('Rolling Mean Coherence', rolling_means_one_month.columns)

    def test_moving_window_saves(self):
        data_dictionary = GetCoherenceGraphsDataDictionary(path_insar, path_ground, path_to_points,
                                                           path_to_save_directory=output_path, location=location,
                                                           site='MUN', subsite='EF', input_data='point').run_method()

        munsary_ef_dataframe = data_dictionary['coherence_ground_dataframe']
        MovingWindow(munsary_ef_dataframe,'Munsary EF',
                                                               munsary_ef_ppt,
                                                               Variable.WATER_CONTENT,
                                                               save_filepath=output_path).get_moving_window()
        self.assertTrue(f'{output_path}/munsary_ef_one_month_window.csv')

    def test_moving_window_dataframe(self):
        data_dictionary = GetCoherenceGraphsDataDictionary(path_insar, path_ground, path_to_points,
                                                           path_to_save_directory=output_path, location=location,
                                                           site='MUN', subsite='EF', input_data='point').run_method()

        munsary_ef_dataframe = data_dictionary['coherence_ground_dataframe']
        moving_window_dictionary = MovingWindow(munsary_ef_dataframe,'Munsary EF',
                                                               munsary_ef_ppt,
                                                               Variable.WATER_CONTENT,
                                                               save_filepath=output_path).get_moving_window()
        self.assertIn('Rolling Mean Water_Content', moving_window_dictionary['one_month_window'].columns)

    def test_moving_window_no_precipitation_dataframe(self):
        data_dictionary = GetCoherenceGraphsDataDictionary(path_insar, path_ground, path_to_points,
                                                           path_to_save_directory=output_path, location=location,
                                                           site='MUN', subsite='EF', input_data='point').run_method()

        munsary_ef_dataframe = data_dictionary['coherence_ground_dataframe']
        moving_window_dictionary = MovingWindow(munsary_ef_dataframe,'Munsary EF',
                                                               None,
                                                               Variable.WATER_CONTENT,
                                                               save_filepath=output_path).get_moving_window()
        self.assertIn('Rolling Mean Water_Content', moving_window_dictionary['one_month_window'].columns)

if __name__ == '__main__':
    unittest.main()
