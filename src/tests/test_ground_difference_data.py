import unittest
import os

from src.GetDFGroundData import GetDFGroundData
from src.GroundDifferenceData import GroundDifferenceData

current_directory = os.getcwd()
path = f'{current_directory}/resources/sample_ground_data'
reference_date = '2018-04-02'

ground_dataframe_water_content = GetDFGroundData(path, data_type='WC', site='MUN', subsite='EF',
                                           variable='Water_Content').get_variable_and_date_specific_csv()

class MyTestCase(unittest.TestCase):
    def test_something(self):
        difference_dataframe = GroundDifferenceData(ground_dataframe=ground_dataframe_water_content, reference_date=reference_date,
                             variable='Water_Content').get_difference_data()
        self.assertIn('Difference_Water_Content', difference_dataframe.columns)


if __name__ == '__main__':
    unittest.main()
