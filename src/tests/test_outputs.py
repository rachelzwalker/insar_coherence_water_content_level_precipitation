import unittest
import os

import src.Outputs
from src.GeoDataFrameLocationCoherence import GeoDataframeLocationCoherence
from src.GetDFGroundData import GetDFGroundData
from src.Outputs import *

current_directory = os.getcwd()
path = f'{current_directory}/resources/sample_ground_data'
path_insar = f'{current_directory}/resources/InSAR_unzipped_sample'
reference_date = '2018-04-02'
path_to_points = f'{current_directory}/resources/shape_file_point'
location = 'Munsary EF'
input_data = 'point'
output_path = f'{current_directory}/resources/outputs'

ground_dataframe_water_content = GetDFGroundData(path, data_type='WC', site='MUN', subsite='EF',
                                                 variable='Water_Content').get_variable_and_date_specific_csv()

coherence_dataframe = GeoDataframeLocationCoherence(path_insar, location=location,
                                                    path_to_points=path_to_points,
                                                    input_data=input_data,
                                                    data_series_dates_to_remove=None).dataframe_coherence()


class MyTestCase(unittest.TestCase):
    def test_merged_dataframe_contains_nans_in_geometry(self):
        coherence_ground_dataframe = src.Outputs.get_merged_dataframe(ground_dataframe_water_content, coherence_dataframe)
        nans_in_geometry = coherence_ground_dataframe.geometry.isnull().sum()
        self.assertGreater(nans_in_geometry, 5)

    def test_scatter_graph_outputted(self):
        coherence_ground_dataframe = src.Outputs.get_merged_dataframe(ground_dataframe_water_content, coherence_dataframe)
        CoherenceGroundScatterGraphs(coherence_ground_dataframe, ['Water_Content'], location=location,
                                     path_to_directory=output_path).graph_scatter_coherence_ground()
        self.assertTrue(f'{output_path}/coherence_ground_scatter_Munsary EF_Water_Content.png')

    def test_line_graph_outputted(self):
        coherence_ground_dataframe = src.Outputs.get_merged_dataframe(ground_dataframe_water_content, coherence_dataframe)
        CoherenceGroundLineGraphs(coherence_ground_dataframe, ['Water_Content'], location=location,
                                     path_to_directory=output_path).graph_coherence_ground_data()
        self.assertTrue(f'{output_path}/coherence_ground_line_Munsary EF_Water_Content.png')


if __name__ == '__main__':
    unittest.main()
