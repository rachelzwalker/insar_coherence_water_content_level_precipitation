import unittest
import os

import src.MovingWindowGraphs
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

data_dictionary = GetCoherenceGraphsDataDictionary(path_insar, path_ground, path_to_points,
                                                   path_to_save_directory=output_path, location=location,
                                                   site='MUN', subsite='EF', input_data='point').run_method()

munsary_ef_dataframe = data_dictionary['coherence_ground_dataframe']
munsary_ef_dataframe = munsary_ef_dataframe.sort_values(by=['Date'])
moving_window_dictionary = MovingWindow(munsary_ef_dataframe, 'Munsary EF',
                                        munsary_ef_ppt,
                                        Variable.WATER_CONTENT,
                                        save_filepath=output_path).get_moving_window()


class MyTestCase(unittest.TestCase):
    def test_something(self):
        src.MovingWindowGraphs.MovingWindowLineGraphs(moving_window_dictionary['one_month_window'], Variable.WATER_CONTENT,
                                                  'munsary_ef',
                                                  src.MovingWindowGraphs.WindowTimeframe.MONTH,
                                                  path_to_directory=output_path,
                                                  n=1).graphs_line()
        self.assertTrue(f'{output_path}/window_r2_normalised_precipitation_1_months_munsary_ef_Water_Content.png')  # add assertion here


if __name__ == '__main__':
    unittest.main()
