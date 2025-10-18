import unittest
import os

import pandas as pd

from src.GetCoherenceGraphsDataDictionary import GetCoherenceGraphsDataDictionary

current_directory = os.getcwd()
path_ground = f'{current_directory}/resources/sample_ground_data'
path_insar = f'{current_directory}/resources/InSAR_unzipped_sample'
reference_date = '2018-04-02'
path_to_points = f'{current_directory}/resources/shape_file_point'
location = 'Munsary EF'
input_data = 'point'
output_path = f'{current_directory}/resources/outputs'


class MyTestCase(unittest.TestCase):
    def test_graphs_saved(self):
        GetCoherenceGraphsDataDictionary(path_insar, path_ground, path_to_points,
                                                           path_to_save_directory=output_path, location=location,
                                                           site='MUN', subsite='EF', input_data='point').run_method()

        self.assertTrue(f'{output_path}/coherence_ground_line_Munsary EF_Temp_Soil.png')

    def test_merged_dataframe(self):
        data_dictionary = GetCoherenceGraphsDataDictionary(path_insar, path_ground, path_to_points,
                                                           path_to_save_directory=output_path, location=location,
                                                           site='MUN', subsite='EF', input_data='point').run_method()

        merged_dataframe = data_dictionary['coherence_ground_dataframe']
        self.assertEqual(len(merged_dataframe.columns), 9)

    def test_returns_two_dataframes(self):
        data_dictionary = GetCoherenceGraphsDataDictionary(path_insar, path_ground, path_to_points,
                                                           path_to_save_directory=output_path, location=location,
                                                           site='MUN', subsite='EF', input_data='point').run_method()

        for key, value in data_dictionary.items(): self.assertTrue(isinstance(value, pd.DataFrame))


if __name__ == '__main__':
    unittest.main()
