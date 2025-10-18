import os

import numpy as np
import pandas as pd
import statsmodels.api as sm
from matplotlib import pyplot as plt
from pandas import DataFrame
from scipy import signal
import seaborn as sns


class DataRelationships:
    def __init__(self, coherence_dataframe: pd.DataFrame,
                 precipitation_dataframe: pd.DataFrame,
                 max_lag:int=-50,
                 second_variable:str='Rolling Mean Precipitation',
                 second_variable_name:str='precipitation',
                 save_file_path:str|None=None,
                 site_name:str|None=None,
                 time_scale:str='1_month'):
        self.coherence_dataframe = coherence_dataframe
        self.precipitation_dataframe = precipitation_dataframe
        self.max_lag = max_lag
        self.second_variable = second_variable
        self.second_variable_name = second_variable_name
        self.save_file_path = save_file_path
        self.site_name = site_name
        self.time_scale = time_scale

    def get_relationships(self) -> dict[str, DataFrame]:
        if self.coherence_dataframe.equals(self.precipitation_dataframe):
            merged_dataframe = self.coherence_dataframe
        else:
            merged_dataframe = self._get_merged_dataframe()

        time_series1 = self._time_series_data(merged_dataframe, 'Rolling Mean Coherence')
        time_series2 = self._time_series_data(merged_dataframe, self.second_variable)
        detrended_series1 = self._detrended_time_series_data(time_series1)
        detrended_series2 = self._detrended_time_series_data(time_series2)

        cross_correlation_time = self._cross_correlation(time_series1, time_series2)

        cross_correlation_detrended = self._cross_correlation(detrended_series1, detrended_series2)

        cross_correlation_scipy = self._cross_correlation_scipy(time_series1, time_series2)

        # self.wavelet_transform_cross_correlation(time_series1, time_series2)
        nlcc_coefficient = self._nlcc(time_series1, time_series2)

        pearson = self.pearson_correlation(merged_dataframe)
        max_cross_correlation = max(cross_correlation_time)
        min_cross_correlation = min(cross_correlation_time)

        pearson_statement = (
            f'Pearson correlation: {pearson}   ')
        max_cross_correlation_statement = (
            f'Max cross_correlation value: {max_cross_correlation}   ')
        min_cross_correlation_statement = (
            f'Min cross_correlation value: {min_cross_correlation}   ')
        max_cross_correlation_statement_scipy = (
            f'Max cross_correlation value scipy: {max(cross_correlation_scipy)}   ')
        nlcc_statement = (f'NLCC: {nlcc_coefficient}')

        lags = np.arange(-len(time_series1) + 1, len(time_series1))
        lags_detrended = np.arange(-len(detrended_series1) + 1, len(detrended_series1))



        if self.save_file_path == None:
            self._plot_cross_corr_with_lags(lags, cross_correlation_time, 'time')
            plt.show()
            self._plot_cross_corr_with_lags(lags_detrended, cross_correlation_detrended, 'detrended')
            plt.show()
            print(pearson_statement)
            print(max_cross_correlation_statement)
            print(min_cross_correlation_statement)
            print(max_cross_correlation_statement_scipy)
            print(nlcc_statement)

        else:
            plt.ioff()
            files_already_exist = []
            full_file_path = f'{self.save_file_path}/cross_correlation_coherence_{self.second_variable_name}_{self.time_scale}_{self.site_name}'
            if os.path.exists(f'{full_file_path}_cross_corr.png'):
                files_already_exist.append(full_file_path)
            else:
                self._plot_cross_corr_with_lags(lags, cross_correlation_time, 'time')
                plt.savefig(f'{full_file_path}_cross_corr.png')
                plt.close()
                self._plot_cross_corr_with_lags(lags_detrended, cross_correlation_detrended, 'detrended')
                plt.savefig(f'{full_file_path}_detrended.png')
                plt.close()
                with open(f'{full_file_path}_summary.txt', 'w') as file:
                    file.writelines(
                        [pearson_statement, max_cross_correlation_statement, min_cross_correlation_statement, max_cross_correlation_statement_scipy,
                         nlcc_statement])

        return {'lags': pd.DataFrame({'lags': lags, 'cross_correlation_time': cross_correlation_time}),
                'metrics': pd.DataFrame({'Site': [self.site_name], 'Pearson': [pearson], 'max_cross_correlation': [max_cross_correlation],
                             'min_cross_correlation': [min_cross_correlation], 'NLCC_coefficient': [nlcc_coefficient]})}


    def pearson_correlation(self, merged_dataframe:pd.DataFrame) -> pd.DataFrame:
        return merged_dataframe['Rolling Mean Coherence'].corr(merged_dataframe[self.second_variable], method='pearson')

    @staticmethod
    def _time_series_data(merged_dataframe: pd.DataFrame, heading:str) -> pd.DataFrame:
        return merged_dataframe[heading]

    @staticmethod
    def _detrended_time_series_data(time_series_data):
        return sm.tsa.detrend(time_series_data)

    @staticmethod
    def _cross_correlation_scipy(time_series1, time_series2):
        return signal.correlate(time_series1, time_series2) / (
                np.linalg.norm(time_series1) * np.linalg.norm(time_series2))

    @staticmethod
    def _cross_correlation(time_series1, time_series2):
        cross_corr = np.correlate(time_series1, time_series2, 'full') / (
                np.linalg.norm(time_series1) * np.linalg.norm(time_series2))
        return cross_corr

    # measure differential of each slope - potential value - skew

    def _plot_cross_corr_with_lags(self, lags, cross_corr, type_to_plot):
        if type_to_plot == 'detrended':
            title = f'Cross-correlation between detrended coherence and {self.second_variable_name}'
        else:
            title = f'Cross-correlation between coherence and {self.second_variable_name}'

        if 'level' in self.second_variable_name:
            colour = '#1f77b4'
        elif 'soil' in self.second_variable_name or 'content' in self.second_variable_name:
            colour = '#17becf'
        else:
            colour = '#1613d5'

        # Plot cross-correlation
        sns.set_theme(style="darkgrid")
        plt.figure()
        plt.plot(lags, cross_corr, color=colour)
        plt.xlabel('Lag')
        plt.ylabel('Cross-correlation')
        plt.title(title)
        plt.grid(True)


    @staticmethod
    def _nlcc(time_series1, time_series2):
        # Calculate NLCC between two signals
        return np.sum(time_series1 * time_series2) / np.sqrt(np.sum(time_series1 ** 2) * np.sum(time_series2 ** 2))

    def _get_merged_dataframe(self) -> pd.DataFrame:
        coherence_dataframe = self._check_index_and_column_names(self.coherence_dataframe)
        precipitation_dataframe = self._check_index_and_column_names(self.precipitation_dataframe)
        return pd.merge(coherence_dataframe, precipitation_dataframe, on='Date', how='inner')

    @staticmethod
    def _check_index_and_column_names(dataframe):
        if dataframe.index.name in dataframe.columns:
            dataframe.index.name = "Date_Index"
            return dataframe
        else:
            return dataframe