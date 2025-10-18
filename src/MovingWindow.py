import numpy as np
import pandas as pd

from enum import Enum


def get_focused_dataframe(dataframe: pd.DataFrame, cols) -> pd.DataFrame:
    dataframe['Date'] = dataframe.index
    focused_dataframe = dataframe[cols]
    focused_dataframe = focused_dataframe.rename(columns={'mean': 'Coherence'})
    return focused_dataframe


def get_moving_window_dataframe(focused_dataframe: pd.DataFrame, n: int, timescale: str) -> pd.DataFrame:
    window_df = focused_dataframe
    if timescale == 'months':
        window_df['EndSubset'] = window_df['Date'] + pd.DateOffset(
            months=n)
    if timescale == 'weeks':
        window_df['EndSubset'] = window_df['Date'] + pd.DateOffset(
            weeks=n)
    return window_df


def get_reduced_dataframe_based_on_window(window_df: pd.DataFrame) -> pd.DataFrame:
    return window_df[~(window_df['EndSubset'] > max(window_df['Date']))]


class GetRollingMean:
    def __init__(self, variable:str|None, core_variable:str='mean'):
        self.variable = variable
        self.core_variable = core_variable

    def rolling_means_with_window(self, dataframe: pd.DataFrame) -> dict:  # to be used if you don't have ground data
        if self.variable == None:
            cols = ['Date', self.core_variable]
        else:
            cols = ['Date', self.core_variable, self.variable]
        focused_dataframe = get_focused_dataframe(dataframe, cols)

        one_month_window_reduced_df = self._rolling_means_window_df(focused_dataframe, 1, 'months')
        six_week_window_reduced_df = self._rolling_means_window_df(focused_dataframe, 6, 'weeks')
        two_month_window_reduced_df = self._rolling_means_window_df(focused_dataframe, 2, 'months')

        return {
            'one_month_rolling_mean_coherence': one_month_window_reduced_df,
            'six_week_rolling_mean_coherence': six_week_window_reduced_df,
            'two_month_rolling_mean_coherence': two_month_window_reduced_df
        }

    def _rolling_means_window_df(self, focused_dataframe: pd.DataFrame, n: int, timescale: str) -> pd.DataFrame:
        window_df = get_moving_window_dataframe(focused_dataframe, n, timescale)
        if self.core_variable == 'mean':
            updated_window_df = self.rolling_means(window_df, 'Coherence')
        else:
            updated_window_df = self.rolling_means(window_df, self.core_variable)
        return get_reduced_dataframe_based_on_window(updated_window_df)

    @staticmethod
    def rolling_means(dataframe: pd.DataFrame, variable) -> pd.DataFrame:  # to be used with the above and below
        dataframe[f'Rolling Mean {variable}'] = dataframe.apply(lambda row: dataframe[
            (row['Date'] <= dataframe['Date']) & (dataframe['Date'] < row['EndSubset'])][
            variable].mean(), axis=1)  # these values are a little different to means calculated in Excel
        return dataframe


class Variable(Enum):
    WATER_CONTENT = 'Water_Content'
    WATER_LEVEL = 'Water_level_meters'
    NONE = 'None'


class MovingWindow:
    def __init__(self, subsite_dataframe: pd.DataFrame, subsite_name: str, precipitation_dataframe: pd.DataFrame|None,
                 variable, save_filepath: str):
        self.dataframe = subsite_dataframe
        self.name = subsite_name
        self.precipitation = precipitation_dataframe
        self.variable = variable.value
        self.filepath = save_filepath

    def get_moving_window(self):
        if self.variable != 'None':
            cols = ['Date', 'mean', self.variable]
        else:
            cols = ['Date', 'mean']
        focused_dataframe = get_focused_dataframe(self.dataframe, cols)
        focused_dataframe = self._get_merged_dataframe(focused_dataframe)

        focused_dataframe = self._get_points_along_graph(focused_dataframe)

        one_month_window_reduced_df = self._get_window_df(focused_dataframe, 1, 'months')
        six_week_window_reduced_df = self._get_window_df(focused_dataframe, 6, 'weeks')
        two_month_window_reduced_df = self._get_window_df(focused_dataframe, 2, 'months')

        if self.variable != 'None':
            one_month_window_reduced_df.to_csv(f'{self.filepath}/{self.name}_one_month_window_{self.variable}.csv')
            six_week_window_reduced_df.to_csv(f'{self.filepath}/{self.name}_six_week_window_{self.variable}.csv')
            two_month_window_reduced_df.to_csv(f'{self.filepath}/{self.name}_two_month_window_{self.variable}.csv')
        else:
            one_month_window_reduced_df.to_csv(f'{self.filepath}/{self.name}_one_month_window_precipitation.csv')
            six_week_window_reduced_df.to_csv(f'{self.filepath}/{self.name}_six_week_window_precipitation.csv')
            two_month_window_reduced_df.to_csv(f'{self.filepath}/{self.name}_two_month_window_precipitation.csv')

        return {
            'one_month_window': one_month_window_reduced_df,
            'six_week_window': six_week_window_reduced_df,
            'two_month_window': two_month_window_reduced_df
        }

    @staticmethod
    def _get_points_along_graph(focused_dataframe: pd.DataFrame) -> pd.DataFrame:
        focused_dataframe['days_difference'] = focused_dataframe['Date'].diff()
        focused_dataframe['days_difference'] = focused_dataframe['days_difference'].fillna(pd.Timedelta(days=0))
        focused_dataframe['point_along_graph'] = focused_dataframe['days_difference'].cumsum()
        focused_dataframe['point_along_graph'] = focused_dataframe['point_along_graph'].dt.days.astype('int16')

        return focused_dataframe

    def _get_window_df(self, focused_dataframe: pd.DataFrame, n: int, timescale: str) -> pd.DataFrame:
        window_df = get_moving_window_dataframe(focused_dataframe, n, timescale)
        window_df = GetRollingMean('Coherence').rolling_means(window_df, 'Coherence')
        if self.variable != 'None':
            window_df = GetRollingMean(self.variable).rolling_means(window_df, self.variable)
        if self.precipitation is not None:
            window_df = GetRollingMean('Precipitation_mm').rolling_means(window_df, 'Precipitation_mm')
        window_df = self._update_window_df(window_df)
        window_reduced_df = get_reduced_dataframe_based_on_window(window_df)
        window_reduced_df = self._add_normalised_column(window_reduced_df, 'normalised_r2', 'r2')
        window_reduced_df = self._add_normalised_column(window_reduced_df, 'normalised_gradient',
                                                         'gradient_changes')
        if self.precipitation is not None:
            window_reduced_df = self._add_normalised_column(window_reduced_df,
                                                         'normalised_precipitation', 'Rolling Mean Precipitation_mm')
        return window_reduced_df

    @staticmethod
    def _add_normalised_column(window_reduced_df: pd.DataFrame, normalised_column_name, column_to_normalise) -> pd.DataFrame:
        window_reduced_df[normalised_column_name] = (window_reduced_df[column_to_normalise] - min(
            window_reduced_df[column_to_normalise])) / (max(
            window_reduced_df[column_to_normalise]) - min(window_reduced_df[column_to_normalise]))
        return window_reduced_df

    def _update_window_df(self, window_df:pd.DataFrame) -> pd.DataFrame:
        r2_score_list = []
        gradient_changes_list = []

        for index, row in window_df.iterrows():
            # Define the date range for the subset
            start_date = row['Date']
            end_date = row['EndSubset']

            # Create a subset based on the date range
            subset = window_df[
                (window_df['Date'] >= start_date) & (window_df['Date'] < end_date)]

            r = subset['Coherence'].corr(subset[self.variable])
            r2 = r ** 2

            r2_score_list.append(r2)

            if self.variable != 'None':
                try:
                    slope, intercept = np.polyfit(subset['Coherence'], subset[self.variable], 1)
                except:
                    subset_clean = subset.dropna(subset=['Coherence', self.variable])
                    subset_clean = subset_clean[
                        np.isfinite(subset_clean['Coherence']) & np.isfinite(subset_clean[self.variable])]
                    slope, intercept = np.polyfit(subset_clean['Coherence'], subset_clean[self.variable], 1)
            else:
                slope, intercept = np.polyfit(subset['Coherence'], subset['Precipitation_mm'], 1)

            y = slope * row['point_along_graph'] + intercept

            gradient_changes_list.append(y)

            # apply normlaisation one in dataframe - to whole column
        window_df['r2'] = r2_score_list
        window_df['gradient_changes'] = gradient_changes_list
        return window_df

    def _get_merged_dataframe(self, focused_dataframe: pd.DataFrame) -> pd.DataFrame:
        # focused_dataframe = focused_dataframe.drop(focused_dataframe.columns[0], axis=1)
        focused_dataframe = focused_dataframe.reset_index(drop=True)
        focused_dataframe['Date'] = pd.to_datetime(focused_dataframe['Date'])
        if self.precipitation is not None:
            focused_dataframe = focused_dataframe.merge(self.precipitation, on='Date')
        # focused_dataframe['Date'] = focused_dataframe.index
        return focused_dataframe
