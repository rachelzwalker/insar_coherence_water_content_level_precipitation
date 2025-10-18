import os

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from scipy.interpolate import UnivariateSpline
import statsmodels.api as sm
import patsy

from src.PolynomialRegression import extract_summary_data_to_df


class Spline:
    def __init__(self, location, path_to_directory=None, dataframes={}, variable='mean', variables_for_comparison=[]):
        self.location = location
        self.path_to_directory = path_to_directory
        self.dataframes = dataframes
        self.variable = variable
        self.variables_for_comparison = variables_for_comparison



    def plot_spline(self):
        files_that_already_exist = []
        for season, dataframe in self.dataframes.items():
            for data in self.variables_for_comparison:
                if data in dataframe.columns:
                    if os.path.exists(
                            f'{self.path_to_directory}/spline_{self.location}_{season}_{data}.png'):
                        files_that_already_exist.append(f'{self.path_to_directory}/spline_{self.location}_{season}_{data}.png')
                    else:
                        X = self.__get_x(dataframe)
                        y = self.__get_y(data, dataframe)

                        X_sorted, y_sorted = self.__get_sorted_indices(X, y)

                        # Fit a spline to the data
                        spline = UnivariateSpline(X_sorted, y_sorted)

                        # Generate a finer set of X values for smoother plotting
                        X_finer = np.linspace(X.min(), X.max(), 1000)

                        # Compute the corresponding y values using the spline
                        y_finer = spline(X_finer)

                        # Plot the original data and the spline curve
                        self.__plot_spline_graph(X, X_finer, data, y, y_finer, season, dataframe)
        return files_that_already_exist

    def get_spline_stats(self):
        stats_dictionary = {}
        for season, dataframe in self.dataframes.items():
            for variable in self.variables_for_comparison:
                if variable in dataframe.columns:
                    X = self.__get_x(dataframe)
                    y = self.__get_y(variable, dataframe)

                    X_sorted, y_sorted = self.__get_sorted_indices(X, y)
                    # Create a DataFrame with sorted data
                    data = pd.DataFrame({'X': X_sorted, 'y': y_sorted})

                    # Using patsy to create the spline basis functions
                    spline_basis = patsy.dmatrix('bs(data["X"], df=4, include_intercept=True)', data=data)

                    # Fit the spline regression model
                    model = sm.OLS(data['y'], spline_basis)
                    result = model.fit()

                    summary = result.summary()

                    ols_df = extract_summary_data_to_df(summary=summary, section_of_summary=0)
                    coef_df = extract_summary_data_to_df(summary=summary, section_of_summary=1)
                    omnibus_df = extract_summary_data_to_df(summary=summary, section_of_summary=2)

                    stats_dictionary[f'Stats summary for {season}: {variable}'] = [ols_df, coef_df, omnibus_df]
        return stats_dictionary

    def __plot_spline_graph(self, X, X_finer, variable, y, y_finer, season, dataframe):
        # Plot the original data and the spline curve
        plt.scatter(X, y, label='Original data', color='blue')
        plt.plot(X_finer, y_finer, label='Spline curve', color='red')
        plt.xlabel('Coherence')
        plt.ylabel(variable)
        plt.title(f'Spline Interpolation of coherence and {variable} for {season} at {self.location}')
        plt.legend()
        if self.path_to_directory == None:
            plt.show()
        else:
            plt.savefig(f'{self.path_to_directory}/spline_{self.location}_{season}_{variable}.png')
            plt.close()

    def __get_sorted_indices(self, X, y):
        # Sort the data for better visualization
        sorted_indices = np.argsort(X)
        X_sorted = X[sorted_indices]
        y_sorted = y[sorted_indices]
        return X_sorted, y_sorted

    def __get_y(self, data, dataframe):
        return dataframe[data].values

    def __get_x(self, dataframe):
        return dataframe[self.variable].values