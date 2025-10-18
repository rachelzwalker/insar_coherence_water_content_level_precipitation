import unittest
import os

from src.GetDFGroundData import GetDFGroundData

current_directory = os.getcwd()
path = f'{current_directory}/resources/sample_ground_data'


class MyTestCase(unittest.TestCase):
    def test_all_water_level_and_temp_water_in_dataframe(self):
        ground_dataframe = GetDFGroundData(path, site='MUN', subsite='EF',
                                           variable='Water_level_meters').create_dataframe_for_whole_csv()
        expected_columns = ['Date', 'Water_level_meters', 'Temp_Water', 'Water_level_meters']
        for column in expected_columns:
            self.assertIn(column, ground_dataframe.columns)

    def test_water_content_in_dataframe(self):
        ground_dataframe_water_content = GetDFGroundData(path, data_type='WC', site='MUN', subsite='EF',
                                           variable='Water_Content').get_variable_and_date_specific_csv()
        self.assertIn('Water_Content', ground_dataframe_water_content.columns)

    def test_temp_soil_not_in_dataframe(self):
        ground_dataframe = GetDFGroundData(path, data_type='WT', site='MUN', subsite='EF',
                                           variable='Water_level_meters').get_variable_and_date_specific_csv()
        self.assertNotIn('Temp_Water', ground_dataframe.columns)


if __name__ == '__main__':
    unittest.main()
