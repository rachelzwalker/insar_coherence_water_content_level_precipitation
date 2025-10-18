import pandas as pd
from enum import Enum


class WindowTimeframe(Enum):
    MONTH = 'months'
    WEEK = 'weeks'


class RollingPrecipitationDataframe:
    def __init__(self, precipitation_dataframe: pd.DataFrame, timescale, precipitation_variable: str = 'prcp',
                 name_of_date_column: str = 'date', number: int = 1):
        self.dataframe = precipitation_dataframe
        self.variable = precipitation_variable
        self.date_column = name_of_date_column
        self.number = number
        self.timescale = timescale.value

    def get_rolling_mean_dataframe(self) -> pd.DataFrame:
        if self.timescale == 'months':
            self._get_end_subset_months()
        if self.timescale == 'weeks':
            self._get_end_subset_weeks()

        self.dataframe['Rolling Mean Precipitation'] = self._get_rolling_mean_precipitation()

        if self.date_column == 'date':
            self.dataframe = self.dataframe.rename(columns={'date': 'Date'})

        return self._remove_n_rows_from_end_rolling_mean()

    def _get_rolling_mean_precipitation(self):
        return self.dataframe.apply(lambda row: self.dataframe[
            (row[self.date_column] <= self.dataframe[self.date_column]) & (
                    self.dataframe[self.date_column] < row['EndSubset'])][
            self.variable].mean(), axis=1)

    def _get_end_subset_months(self):
        self.dataframe['EndSubset'] = self.dataframe[self.date_column] + pd.DateOffset(months=self.number,
                                                                                       normalize=True)

    def _get_end_subset_weeks(self):
        self.dataframe['EndSubset'] = self.dataframe[self.date_column] + pd.DateOffset(weeks=self.number,
                                                                                       normalize=True)

    def _remove_n_rows_from_end_rolling_mean(self):
        count_exceeding_max = len(self.dataframe[self.dataframe['EndSubset'] > self.dataframe['Date'].max()])
        return self.dataframe.iloc[:-count_exceeding_max]
