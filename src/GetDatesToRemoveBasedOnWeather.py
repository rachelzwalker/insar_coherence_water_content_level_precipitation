from enum import Enum

import pandas as pd


class WeatherAspect(Enum):
    PRECIPITATION_AMOUNT = 'precipitation_amount'
    PRECIPITATION_TIME = 'precipitation_time'
    TEMPERATURE = 'temperature'
    TEMPERATURE_AND_PRECIPITATION_AMOUNT = 'both'
    TEMPERATURE_AND_PRECIPITATION_TIME = 'temp_time'
    TEMPERATURE_AND_PRECIPITATION_TIME_AMOUNT = 'temp_time_amount'
    PRECIPITATION_TIME_AMOUNT = 'precipitation_time_amount'
    SNOW_ONLY = 'snow'
    NONE = 'none'

class GetDatesToRemoveBasedOnWeather:
    def __init__(self, dataframe: pd.DataFrame, weather_aspect, temperature_column_name: str = 'tavg',
                 date_column_name: str = 'date'):
        self.dataframe = dataframe
        self.weather_aspect = weather_aspect.value
        self.temperature_column_name = temperature_column_name
        self.date_column_name = date_column_name


    def get_dates_to_remove_from_coherence_data(self) -> pd.DataFrame:
        if 'snow' in self.dataframe.columns:
            snow_filter_prior_to_other_removal = self.dataframe[self.dataframe['snow'] == 0]
        else:
            snow_filter_prior_to_other_removal = self.dataframe.copy()
        if self.weather_aspect == 'temperature':
            filtered_dataframe = self._get_less_than_filtered_dataframe(snow_filter_prior_to_other_removal, 2)
        elif self.weather_aspect == 'precipitation_amount':
            filtered_dataframe = self._get_more_than_filtered_dataframe(snow_filter_prior_to_other_removal, 20)
        elif self.weather_aspect == 'both':
            temperature_filtered_dataframe = self._get_less_than_filtered_dataframe(snow_filter_prior_to_other_removal,
                                                                                    2)
            precipitation_filtered_dataframe = self._get_more_than_filtered_dataframe(snow_filter_prior_to_other_removal,
                                                                                      20)
            filtered_dataframe = self._concat_two_dataframes_same_columns(temperature_filtered_dataframe,
                                                                          precipitation_filtered_dataframe)
        elif self.weather_aspect == 'precipitation_time':
            filtered_dataframe = self.get_where_rained_within_6_hours(snow_filter_prior_to_other_removal)
        elif self.weather_aspect == 'temp_time':
            temperature_filtered_dataframe = self._get_less_than_filtered_dataframe(snow_filter_prior_to_other_removal,
                                                                                    2)
            precipitation_filtered_dataframe = self.get_where_rained_within_6_hours(snow_filter_prior_to_other_removal)
            filtered_dataframe = self._concat_two_dataframes_same_columns(temperature_filtered_dataframe,
                                                                          precipitation_filtered_dataframe)
        elif self.weather_aspect == 'precipitation_time_amount':
            precipitation_time_filtered_dataframe = self.get_where_rained_within_6_hours(
                snow_filter_prior_to_other_removal)
            precipitation_amount_filtered_dataframe = self._get_more_than_filtered_dataframe(
                snow_filter_prior_to_other_removal, 20)
            filtered_dataframe = self._concat_two_dataframes_same_columns(precipitation_time_filtered_dataframe,
                                                                          precipitation_amount_filtered_dataframe)
        elif self.weather_aspect == 'temp_time_amount':
            temperature_filtered_dataframe = self._get_less_than_filtered_dataframe(snow_filter_prior_to_other_removal,
                                                                                    2)
            precipitation_time_filtered_dataframe = self.get_where_rained_within_6_hours(
                snow_filter_prior_to_other_removal)
            precipitation_amount_filtered_dataframe = self._get_more_than_filtered_dataframe(
                snow_filter_prior_to_other_removal, 20)
            filtered_dataframe = self._concat_two_dataframes_same_columns(temperature_filtered_dataframe,
                                                                          precipitation_time_filtered_dataframe)
            filtered_dataframe = self._concat_two_dataframes_same_columns(filtered_dataframe,
                                                                          precipitation_amount_filtered_dataframe)

        else:
            filtered_dataframe = pd.DataFrame(columns=self.dataframe.columns)

        if 'snow' in filtered_dataframe.columns:
            snow_dates_to_remove = self.dataframe[self.dataframe['snow'] > 0]
        else:
            snow_dates_to_remove = filtered_dataframe.copy()
        snow_with_dates_to_remove = self._concat_two_dataframes_same_columns(filtered_dataframe, snow_dates_to_remove)
        if self.weather_aspect == 'none':
            snow_with_dates_to_remove = pd.DataFrame(columns=self.dataframe.columns)
        return snow_with_dates_to_remove[self.date_column_name]

    def get_where_rained_within_6_hours(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        if dataframe.duplicated(subset=[self.date_column_name]).sum() != 0:
            try:
                dataframe[self.date_column_name] = pd.to_datetime(dataframe[self.date_column_name],
                                                              dayfirst=True)  # Convert from DD/MM/YYYY to YYYY-MM-DD
            except Exception as e:
                print(f"Initial parsing failed with error: {e}")
                print("Falling back to MM/DD/YYYY format.")
                dataframe[self.date_column_name] = pd.to_datetime(dataframe[self.date_column_name], format='%m/%d/%Y',
                                                             errors='coerce')
            dataframe[self.date_column_name] = dataframe[self.date_column_name].dt.strftime(
                '%m/%d/%Y')  # Convert from YYYY-MM-DD to MM/DD/YYYY
            dataframe['Datetime'] = pd.to_datetime(dataframe[self.date_column_name] + ' ' + dataframe['Time'])
            # Create an empty DataFrame to store the rows to keep
            dates_to_remove = pd.DataFrame()
            # Iterate over the unique dates
            for date in dataframe['Datetime'].dt.date.unique():
                # Select rows within the previous 6 hours to 1800 (6 PM)
                start_time = pd.Timestamp(date.year, date.month, date.day, 12)  # 6 hours before 1800 is 1200 (12 PM)
                end_time = pd.Timestamp(date.year, date.month, date.day, 18)  # 1800 is 18 in 24-hour format
                mask = (dataframe['Datetime'] >= start_time) & (dataframe['Datetime'] <= end_time)
                subset = dataframe.loc[mask]

                # Check if the sum of the prcp column is more than 0
                if subset['prcp'].sum() > 0:
                    dates_to_remove = pd.concat([dates_to_remove, subset])

            # Return the DataFrame with the rows where the sum of prcp was more than 0 in the 6 hours before 1800
            return dates_to_remove
        return pd.DataFrame(columns=dataframe.columns)

    @staticmethod
    def _concat_two_dataframes_same_columns(dataframe1: pd.DataFrame, dataframe2: pd.DataFrame) -> pd.DataFrame:
        combined_dataframe = pd.concat([dataframe1, dataframe2], axis=0)
        return combined_dataframe.drop_duplicates()

    def _get_less_than_filtered_dataframe(self, dataframe: pd.DataFrame, temperature: int) -> pd.DataFrame:
        return dataframe[dataframe[self.temperature_column_name] < temperature]

    def _get_more_than_filtered_dataframe(self, dataframe: pd.DataFrame, data: int) -> pd.DataFrame:
        if dataframe.duplicated(subset=[self.date_column_name]).sum() != 0:
            try:
                dataframe[self.date_column_name] = pd.to_datetime(dataframe[self.date_column_name],
                                                              dayfirst=True)  # Convert from DD/MM/YYYY to YYYY-MM-DD
            except Exception as e:
                print(f"Initial parsing failed with error: {e}")
                print("Falling back to MM/DD/YYYY format.")
                dataframe[self.date_column_name] = pd.to_datetime(dataframe[self.date_column_name], format='%m/%d/%Y',
                                                             errors='coerce')

            dataframe[self.date_column_name] = dataframe[self.date_column_name].dt.strftime(
                '%m/%d/%Y')  # Convert from YYYY-MM-DD to MM/DD/YYYY
            dataframe['Datetime'] = pd.to_datetime(dataframe[self.date_column_name] + ' ' + dataframe['Time'])
            dataframe['Period'] = dataframe['Datetime'] - pd.to_timedelta(dataframe['Datetime'].dt.hour - 18, unit='h')
            dataframe['Period'] = dataframe['Period'].dt.floor('D')
            result = dataframe.groupby('Period')['prcp'].sum()
            period_dataframe = result.to_frame()
            dates_to_remove = period_dataframe[period_dataframe['prcp'] > data]
            dates_to_remove[self.date_column_name] = dates_to_remove.index
            dates = dates_to_remove[self.date_column_name]
            return dataframe[dataframe[self.date_column_name].isin(dates)]
        return dataframe[dataframe['prcp'] > data]
