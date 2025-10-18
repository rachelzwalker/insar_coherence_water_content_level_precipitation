import unittest
import os

from src.ListOfFiles import get_list_of_files, GetListShapefiles

current_directory = os.getcwd()
resources_directory = f'{current_directory}/resources/shape_file_point'

class MyTestCase(unittest.TestCase):
    def test_get_list_of_files(self):
        list_of_files = get_list_of_files(resources_directory)
        self.assertIsInstance(list_of_files, list)

    def test_number_of_files(self):
        list_of_files = get_list_of_files(resources_directory)
        self.assertEqual(len(list_of_files), 114)

    def test_number_of_shape_files(self):
        list_shapefiles = GetListShapefiles(shape_file_path=resources_directory).get_list_of_shapefiles()
        self.assertEqual(len(list_shapefiles), 23)

    def test_get_focused_name_of_site_not_whole_path(self):
        list_shapefiles = GetListShapefiles(shape_file_path=resources_directory).get_list_of_shapefiles()
        self.assertIn('Site_Munsary EF.shp', list_shapefiles)

if __name__ == '__main__':
    unittest.main()
