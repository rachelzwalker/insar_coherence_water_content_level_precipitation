import unittest
import os

from src.DirectorySearchTiff import DirectorySearchTif

current_directory = os.getcwd()
path = f'{current_directory}/resources/InSAR_unzipped_sample'


class MyTestCase(unittest.TestCase):
    def test_check_number_of_tifs(self):
        list_of_tiffs = DirectorySearchTif(root_directory=path, sentinel_focus=None).get_tifs()
        self.assertEqual(len(list_of_tiffs), 15)  # add assertion here

    def test_name_of_first_tif(self):
        list_of_tiffs = DirectorySearchTif(root_directory=path, sentinel_focus=None).get_tifs()
        expected_name = '/home/rachel/local_python/insar_coherence_water_content_level_precipitation/src/tests/resources/InSAR_unzipped_sample/S1AB_20170531T175103_20180402T175024_VVP306_INT40_G_weF_125D/S1AB_20170531T175103_20180402T175024_VVP306_INT40_G_weF_125D_corr.tif'
        self.assertEqual(expected_name, list_of_tiffs[0])


if __name__ == '__main__':
    unittest.main()
