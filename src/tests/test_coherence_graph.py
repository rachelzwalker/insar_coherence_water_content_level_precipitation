import unittest
import os

import pandas as pd

from src.GeoDataFrameLocationCoherence import GeoDataframeLocationCoherence
from src.CoherenceGraph import CoherenceGraph

current_directory = os.getcwd()
path = f'{current_directory}/resources/InSAR_unzipped_sample'

path_to_points = f'{current_directory}/resources/shape_file_point'
location = 'Munsary EF'
input_data = 'point'
output_path = f'{current_directory}/resources/outputs'

coherence_dataframe = GeoDataframeLocationCoherence(path, location=location,
                                                    path_to_points=path_to_points,
                                                    input_data=input_data,
                                                    data_series_dates_to_remove=None).dataframe_coherence()


class MyTestCase(unittest.TestCase):
    def test_graph(self):
        CoherenceGraph(geodataframe=coherence_dataframe, location=location, input_data=input_data,
                       output_path=output_path).graph()
        self.assertTrue(f'{output_path}/mean_coherence_Munsary EF.png')

    def test_dataframe_only_dropped_geometry_column(self):
        mean_dataframe = CoherenceGraph(geodataframe=coherence_dataframe, location=location, input_data=input_data,
                       output_path=output_path).mean_dataframe(coherence_dataframe)
        self.assertEqual(len(mean_dataframe.columns), len(coherence_dataframe.columns)-1)


if __name__ == '__main__':
    unittest.main()
