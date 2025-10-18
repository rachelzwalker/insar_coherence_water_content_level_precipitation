import unittest
import os

import pandas as pd

from src.GeoDataFrameLocationCoherence import GeoDataframeLocationCoherence

current_directory = os.getcwd()
path = f'{current_directory}/resources/InSAR_unzipped_sample'
path_to_points = f'{current_directory}/resources/shape_file_point'
path_to_polygon = f'{current_directory}/resources/shape_file_polygon/Site_Munsary.shp'


class MyTestCase(unittest.TestCase):
    def test_length_coherence_dataframe(self):
        coherence_dataframe = GeoDataframeLocationCoherence(path, location='Munsary EF',
                                                            path_to_points=path_to_points,
                                                            input_data='point',
                                                            data_series_dates_to_remove=None).dataframe_coherence()
        self.assertEqual(len(coherence_dataframe), 15)

    def test_columns_coherence_dataframe(self):
        coherence_dataframe = GeoDataframeLocationCoherence(path, location='Munsary EF',
                                                            path_to_points=path_to_points,
                                                            input_data='point',
                                                            data_series_dates_to_remove=None).dataframe_coherence()
        self.assertEqual(list(coherence_dataframe.columns), ['geometry', 'mean'])

    def test_dates(self):
        coherence_dataframe = GeoDataframeLocationCoherence(path, location='Munsary EF',
                                                            path_to_points=path_to_points,
                                                            input_data='point',
                                                            data_series_dates_to_remove=None).dataframe_coherence()
        dates_column = coherence_dataframe.index
        self.assertTrue(isinstance(dates_column[0], pd.Timestamp))

    # def test_polygon(self):
    #     coherence_dataframe = GeoDataframeLocationCoherence(path, location='Munsary',
    #                                                         path_to_points=path_to_polygon,
    #                                                         input_data='polygon',
    #                                                         data_series_dates_to_remove=None).dataframe_coherence()
    #     self.assertIn(['geometry', 'mean'], list(coherence_dataframe.columns))

if __name__ == '__main__':
    unittest.main()
