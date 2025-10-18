import unittest
import pandas as pd
import os

from src.GetDatesToRemoveBasedOnWeather import GetDatesToRemoveBasedOnWeather, WeatherAspect

current_directory = os.getcwd()
path_ground = f'{current_directory}/resources/sample_ground_data'

munsary_ef_weather = pd.read_csv(f'{path_ground}/MUN_ENV_SITEEF.csv')

WEATHER_ASPECT_TO_REMOVE = WeatherAspect.TEMPERATURE
WEATHER_TEMPERATURE_COLUMN_HEADING = 'Temp_Soil'

class MyTestCase(unittest.TestCase):
    def test_something(self):
        dates_to_remove_dataframe = GetDatesToRemoveBasedOnWeather(munsary_ef_weather, WEATHER_ASPECT_TO_REMOVE, WEATHER_TEMPERATURE_COLUMN_HEADING,
                                       date_column_name='Date').get_dates_to_remove_from_coherence_data()
        self.assertLess(len(dates_to_remove_dataframe), len(munsary_ef_weather))  # add assertion here


if __name__ == '__main__':
    unittest.main()
