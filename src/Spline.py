import pandas as pd
from scipy.interpolate import make_interp_spline


class Spline:
    def __init__(self, dataframe: pd.DataFrame, variable_to_spline, variable_name_for_column: str,
                 frequency: str = '1M', k: int = 2):
        self.dataframe = dataframe
        self.variable = variable_to_spline
        self.name = variable_name_for_column
        self.frequency = frequency
        self.k = k

    def get_spline_dataframe(self):
        self.dataframe = self.dataframe.sort_values(by=['Date'])
        x_smooth = pd.date_range(self.dataframe['Date'].min(), self.dataframe['Date'].max(), freq=self.frequency)
        y_smooth = make_interp_spline(self.dataframe['Date'], self.dataframe[self.variable], k=self.k)(x_smooth)
        if 'M' in self.frequency:
            smoothed_dataframe = pd.DataFrame({'Month': x_smooth, self.name: y_smooth})
        elif 'W' in self.frequency:
            smoothed_dataframe = pd.DataFrame({'Week': x_smooth, self.name: y_smooth})
        else:
            smoothed_dataframe = 'Error: Check frequency - should include M or W'
        return smoothed_dataframe
