import unittest
import os

from src import SplitData
from src.GetDFGroundData import GetDFGroundData

current_directory = os.getcwd()
path = f'{current_directory}/resources/sample_ground_data'

ground_dataframe = GetDFGroundData(path, site='MUN', subsite='1',
                                           variable='Water_level_meters').create_dataframe_for_whole_csv()

class MyTestCase(unittest.TestCase):
    def test_focus_to_time_period(self):
        start_date = '2021-08-26'
        end_date = '2021-09-27'
        focused_dataframe = SplitData.focus_data(ground_dataframe, start_date, end_date)
        self.assertLess(len(focused_dataframe), len(ground_dataframe))  # add assertion here

    def test_split_into_seasons_size(self):
        seasons_dictionary = SplitData.split_seasons(ground_dataframe)
        winter_dataframe = seasons_dictionary['winter']
        self.assertLess(len(winter_dataframe), len(ground_dataframe))

    def test_split_into_seasons_dates(self):
        seasons_dictionary = SplitData.split_seasons(ground_dataframe)
        winter_dataframe = seasons_dictionary['winter']
        unique_months_numeric = winter_dataframe['Date'].dt.month.unique().tolist()
        self.assertIn(1, unique_months_numeric)

    def test_split_into_seasons_dates_not_in(self):
        seasons_dictionary = SplitData.split_seasons(ground_dataframe)
        winter_dataframe = seasons_dictionary['winter']
        unique_months_numeric = winter_dataframe['Date'].dt.month.unique().tolist()
        self.assertNotIn(7, unique_months_numeric)

    def test_split_into_seasons_dates_number_months(self):
        seasons_dictionary = SplitData.split_seasons(ground_dataframe)
        winter_dataframe = seasons_dictionary['winter']
        unique_months_numeric = winter_dataframe['Date'].dt.month.unique().tolist()
        self.assertEqual(len(unique_months_numeric), 3)

    def test_split_into_warmer_coolers(self):
        year_split_in_half = SplitData.split_warm_cooler(ground_dataframe)
        warmer_dataframe = year_split_in_half['warmer_months']
        unique_months_numeric = warmer_dataframe['Date'].dt.month.unique().tolist()
        self.assertEqual(len(unique_months_numeric), 6)

    def test_split_into_months_by_year(self):
        month_year_dictionary = SplitData.split_months_for_each_year(ground_dataframe)
        self.assertIn(2021, month_year_dictionary.keys())

if __name__ == '__main__':
    unittest.main()
