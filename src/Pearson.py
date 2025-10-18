import os

import matplotlib.pyplot as plt
import pandas as pd
from scipy.stats import linregress
from scipy.stats import pearsonr


class Pearson:
    def __init__(self, location, path_to_directory=None, dataframes={}, variable='mean', variables_for_comparison=[]):
        self.location = location
        self.path_to_directory = path_to_directory
        self.dataframes = dataframes
        self.variable = variable
        self.variables_for_comparison = variables_for_comparison

    def get_correlation_coefficient_and_p_value(self):
        summary_dataframe = pd.DataFrame(columns=['', 'Variable', 'Correlation coefficient', 'p value'])

        for season, dataframe in self.dataframes.items():
            for data in self.variables_for_comparison:
                if data in dataframe.columns:
                    correlation_coefficient, p_value = pearsonr(dataframe[data], dataframe[self.variable])
                    new_row = pd.Series(
                        {'': season, 'Variable': data, 'Correlation coefficient': correlation_coefficient,
                         'p value': p_value})
                    summary_dataframe = self.__append_row(summary_dataframe, new_row)
        return summary_dataframe.sort_values('p value', ascending=True)

    def plot_pearson(self):
        files_that_already_exist = []
        for season, dataframe in self.dataframes.items():
            for data in self.variables_for_comparison:
                if data in dataframe.columns:
                    if os.path.exists(f'{self.path_to_directory}/pearson_plot_{self.location}_{season}_{data}.png'):
                        files_that_already_exist.append(f'{self.path_to_directory}/pearson_plot_{self.location}_{season}_{data}.png')
                    else:
                        x = dataframe[self.variable].values
                        y = dataframe[data].values

                        # Calculate the line of best fit
                        slope, intercept, r_value, p_value, std_err = linregress(x, y)
                        line = slope * x + intercept

                        # Calculate R-squared value
                        r_squared = r_value ** 2

                        self.__plot_data(x, y, line, r_value, r_squared, data, season)

        return files_that_already_exist

    def __plot_data(self, x, y, line, r_value, r_squared, data, season):
        # Create scatter plot
        plt.scatter(x, y, color='blue', label='Data Points')
        plt.plot(x, line, color='red', label='Line of Best Fit')

        # Get the current axis limits
        x_min, x_max = plt.xlim()
        y_min, y_max = plt.ylim()

        # Define the position for text
        text_x = x_max - 0.7 * (x_max - x_min)  # 50% from right
        text_y1 = y_max - 0.9 * (y_max - y_min)  # 10% from top
        text_y2 = y_max - 0.93 * (y_max - y_min)  # 10% from top

        # Display the statistical values in the plot
        plt.text(text_x, text_y1, f"Pearson's r: {r_value:.2f}", fontsize=10)
        plt.text(text_x, text_y2, f"R-squared: {r_squared:.2f}", fontsize=10)

        # Set labels and title
        plt.xlabel('Coherence')
        plt.ylabel(data)
        plt.title(f'Scatter plot of coherence and {data} for {season} at {self.location}')

        # Display legend
        plt.legend()

        if self.path_to_directory == None:
            plt.show()
        else:
            plt.savefig(f'{self.path_to_directory}/pearson_plot_{self.location}_{season}_{data}.png')
            plt.close()

    def __append_row(self, dataframe, row):
        return pd.concat([dataframe, pd.DataFrame([row], columns=row.index)]).reset_index(drop=True)
