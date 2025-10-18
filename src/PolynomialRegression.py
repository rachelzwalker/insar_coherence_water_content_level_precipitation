import os

import numpy as np
import pandas as pd
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
import statsmodels.api as sm


def extract_summary_data_to_df(summary, section_of_summary):
    table = summary.tables[section_of_summary]
    data_to_input = table.data
    headers = data_to_input[0]
    values = data_to_input[1:]
    dataframe = pd.DataFrame(values, columns=headers)
    return dataframe

class PolynomialRegression:
    def __init__(self, location, path_to_directory=None, dataframes={}, variable='mean', variables_for_comparison=[], degree=2):
        self.location = location
        self.path_to_directory = path_to_directory
        self.dataframes = dataframes
        self.variable = variable
        self.variables_for_comparison = variables_for_comparison
        self.degree = degree

    def plot_polynomial_regression(self):
        files_that_already_exist = []
        for season, dataframe in self.dataframes.items():
            for data in self.variables_for_comparison:
                if data in dataframe.columns:
                    if os.path.exists(f'{self.path_to_directory}/polynomial_regression_{self.location}_{season}_{data}.png'):
                        files_that_already_exist.append(f'{self.path_to_directory}/polynomial_regression_{self.location}_{season}_{data}.png')
                    else:
                        X = self.__get_x(dataframe)
                        y = self.__get_y(data, dataframe)

                        # Creating polynomial features
                        poly_features = self.__create_polynomial_features()
                        X_poly = self.__get_X_polynomial_features(X, poly_features)

                        # Fitting the polynomial regression model
                        model = LinearRegression()
                        model.fit(X_poly, y)

                        # Predicting on the same data for visualization
                        y_pred = model.predict(X_poly)

                        self.__plot_data(X, data, model, poly_features, y, season, dataframe)
        return files_that_already_exist

    def get_stats_polynomial_regression(self):
        stats_dictionary = {}
        for season, dataframe in self.dataframes.items():
            for data in self.variables_for_comparison:
                if data in dataframe.columns:
                    X = self.__get_x(dataframe)
                    y = self.__get_y(data, dataframe)

                    # Creating polynomial features
                    poly_features = self.__create_polynomial_features()
                    X_poly = self.__get_X_polynomial_features(X, poly_features)

                    # Using statsmodels to get the p-value for the overall model
                    X_poly_stats = sm.add_constant(X_poly)  # Adding a constant term for intercept
                    model_stats = sm.OLS(y, X_poly_stats).fit()

                    summary = model_stats.summary()

                    ols_df = extract_summary_data_to_df(summary=summary, section_of_summary=0)
                    coef_df = extract_summary_data_to_df(summary=summary, section_of_summary=1)
                    omnibus_df = extract_summary_data_to_df(summary=summary, section_of_summary=2)

                    stats_dictionary[f'Stats summary for {season}: {data}'] = [ols_df, coef_df, omnibus_df]
        return stats_dictionary

    def __get_X_polynomial_features(self, X, poly_features):
        return poly_features.fit_transform(X)

    def __create_polynomial_features(self):
        return PolynomialFeatures(degree=self.degree)

    def __plot_data(self, X, data, model, poly_features, y, season, dataframe):
        # Plotting the original data points
        plt.scatter(X, y, color='blue', label=data)
        # Sort X for better visualization of the fitted curve
        X_sorted = np.sort(X, axis=0)
        y_pred_sorted = model.predict(poly_features.fit_transform(X_sorted))
        # Plotting the fitted polynomial curve
        plt.plot(X_sorted, y_pred_sorted, color='red', label=f'Polynomial Regression (Degree {self.degree})')
        plt.xlabel('Coherence')
        plt.ylabel(data)
        plt.title(f'Polynomial Regression of coherence and {data} for {season} at {self.location}')
        plt.legend()
        if self.path_to_directory == None:
            plt.show()
        else:
            plt.savefig(f'{self.path_to_directory}/polynomial_regression_{self.location}_{season}_{data}.png')
            plt.close()


    def __get_y(self, data, dataframe):
        return dataframe[data].values

    def __get_x(self, dataframe):
        return dataframe[self.variable].values.reshape(-1, 1)
