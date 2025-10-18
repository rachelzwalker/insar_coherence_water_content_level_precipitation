import os
from textwrap import wrap

import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt
from scipy.stats import linregress
from enum import Enum
from matplotlib import dates as mdates


class Variable(Enum):
    WATER_CONTENT = 'Water_Content'
    WATER_LEVEL = 'Water_level_meters'
    NONE = 'None'


class WindowTimeframe(Enum):
    MONTH = 'months'
    WEEK = 'weeks'


class MovingWindowScatterGraphs:
    def __init__(self, dataframe: pd.DataFrame, variable, location: str, window_timeframe,
                 path_to_directory: str | None = None, n: int = 1, figsize: tuple[float] = (6.4, 4.8)):
        self.location = location
        self.path_to_directory = path_to_directory
        self.dataframe = dataframe
        self.variable = variable.value
        self.timeframe = window_timeframe.value
        self.n = n
        self.figsize = figsize
        self.r2_p_dictionary = {}

        if 'level' in self.variable:
            self.colour = '#1f77b4'
        elif 'soil' in self.variable or 'content' in self.variable:
            self.colour = '#17becf'
        else:
            self.colour = '#1613d5'


    def graph_scatter(self) -> None:
        y = self.__get_y()
        name = 'Rolling Mean Coherence'
        if y in self.dataframe:
            if self.path_to_directory == None:
                r2, p =self._get_plot(y, name)
                print(f'R2:{r2:.3f}, p:{p:.3f}')
                plt.show()
            else:
                plt.ioff()
                files_already_exist = []
                full_file_path = f'{self.path_to_directory}/window_coherence_{self.variable}_{self.n}_{self.timeframe}_{self.location}.png'
                if os.path.exists(full_file_path):
                    files_already_exist.append(full_file_path)
                else:
                    r2, p = self._get_plot(y, name)
                    self.r2_p_dictionary[full_file_path] = {'r2': r2, 'p': p}
                    plt.savefig(full_file_path)
                    plt.close()
            if 'Date' in self.dataframe.columns:
                self._graph_seasons_scatter()
        self._r2_p_to_csv()

    def _r2_p_to_csv(self):
        df = pd.DataFrame.from_dict(self.r2_p_dictionary, orient='index')
        df.to_csv(f'{self.path_to_directory}/window_coherence_r2_p_values.csv')

    def _graph_seasons_scatter(self):
        y = self.__get_y()
        name = 'Rolling Mean Coherence'

        if y not in self.dataframe:
            return

        self.dataframe['Date'] = pd.to_datetime(self.dataframe['Date'])

        # Add season and half-year columns
        self.dataframe['Month'] = self.dataframe['Date'].dt.month
        self.dataframe['Season'] = self.dataframe['Month'].map({
            12: 'Winter', 1: 'Winter', 2: 'Winter',
            3: 'Spring', 4: 'Spring', 5: 'Spring',
            6: 'Summer', 7: 'Summer', 8: 'Summer',
            9: 'Fall', 10: 'Fall', 11: 'Fall'
        })

        # Define warmer (Apr-Sep) and cooler (Oct-Mar) halves
        self.dataframe['Half_Year'] = self.dataframe['Month'].apply(
            lambda x: 'Warmer' if 4 <= x <= 9 else 'Cooler'
        )

        # Create graphs by season
        seasons = ['Spring', 'Summer', 'Fall', 'Winter']
        for season in seasons:
            season_data = self.dataframe[self.dataframe['Season'] == season]
            if not season_data.empty:
                self._create_seasonal_plot(season_data, name, y,season)

        # Create graphs by half-year
        half_years = ['Warmer', 'Cooler']
        for half in half_years:
            half_data = self.dataframe[self.dataframe['Half_Year'] == half]
            if not half_data.empty:
                self._create_seasonal_plot(half_data, name, y, half.lower())

    def _create_seasonal_plot(self, data, name, y, suffix):
        """Helper method to create individual seasonal plots"""
        if self.path_to_directory == None:
            # Create plot using the existing method but with filtered data
            temp_df = self.dataframe.copy()
            self.dataframe = data
            r2, p = self._get_plot(y, name)
            print(f'R2:{r2:.3f}, p:{p:.3f}')
            self.dataframe = temp_df  # Restore original dataframe
            plt.show()
            plt.show()
        else:
            plt.ioff()
            files_already_exist = []
            full_file_path = f'{self.path_to_directory}/window_coherence_{self.variable}_{self.n}_{self.timeframe}_{self.location}_{suffix}.png'

            if os.path.exists(full_file_path):
                files_already_exist.append(full_file_path)
            else:
                # Create plot using the existing method but with filtered data
                temp_df = self.dataframe.copy()
                self.dataframe = data
                r2, p = self._get_plot(y, name)
                self.dataframe = temp_df  # Restore original dataframe
                plt.savefig(full_file_path)
                self.r2_p_dictionary[full_file_path] = {'r2': r2, 'p': p}
                plt.close()



    def _get_plot(self, y, name):
        sns.set_theme(style="darkgrid")
        _, ax = plt.subplots(figsize=self.figsize)
        x = self.dataframe[name]
        ax.scatter(x, self.dataframe[y], color=self.colour)

        slope, intercept, r_value, p_value, _ = linregress(x, self.dataframe[y])
        r_squared = r_value ** 2
        trendline = slope * x + intercept
        plt.plot(x, trendline, color='red', label='Trend Line')
        ax.text(0.05, 0.9, f'R² = {r_squared:.2f}', transform=ax.transAxes, fontsize=12, color='black')
        plt.xlabel(name)
        if self.variable == 'Water_Content':
            plt.ylabel('Rolling Mean Soil Moisture (mg/g)')
        if self.variable == 'Water_level_meters':
            plt.ylabel('Rolling Mean Water Level (m)')
        plt.tight_layout()
        return r_squared, p_value

    def __get_y(self):
        if self.variable == 'Water_Content':
            return 'Rolling Mean Water_Content'
        if self.variable == 'Water_level_meters':
            return 'Rolling Mean Water_level_meters'


class MovingWindowLineGraphs:
    def __init__(self, dataframe, variable, location, timeframe, path_to_directory=None, n=1,
                 figsize=(6.4, 4.8)):
        self.location = location
        self.path_to_directory = path_to_directory
        self.dataframe = dataframe
        self.variable = variable.value
        self.timeframe = timeframe.value
        self.n = n
        self.figsize = figsize
        self.season_colors = {
                    "Winter": "powderblue",  # December - February
                    "Spring": "white",        # March - May (No shading)
                    "Summer": "moccasin",   # June - August
                    "Autumn": "white",        # September - November (No shading)
                }

    def graphs_line(self):
        self.rolling_mean_line_graph()
        self.graph_rolling_coherence_ground_data()

    def rolling_mean_line_graph(self) -> None:
        y1 = 'Rolling Mean Coherence'
        y2 = self._get_y_label()
        y2_label = self._get_y_label_with_units()

        if y2 in self.dataframe:
            if self.path_to_directory == None:
                self._get_plot_2y(y1, y2, y2_label)
                plt.show()
            else:
                plt.ioff()
                files_already_exist = []
                full_file_path = f'{self.path_to_directory}/window_{y1}_{y2}_{self.n}_{self.timeframe}_{self.location}.png'

                if os.path.exists(full_file_path):
                    files_already_exist.append(full_file_path)
                else:
                    self._get_plot_2y(y1, y2, y2_label)
                    plt.savefig(full_file_path)
                    plt.close()

    def _get_plot_2y(self, y1: str, y2: str, y2_label: str):
        _, ax1 = plt.subplots()
        color = 'navy'
        ax1.set_xlabel('Date')
        ax1.set_ylabel(y1, color=color)
        ax1.plot(self.dataframe['Date'], self.dataframe[y1], color=color)
        ax1.tick_params(axis='y', labelcolor=color)
        # Create the second plot with 'Y2' on the secondary y-axis
        ax2 = ax1.twinx()
        color = self.colour
        ax2.set_ylabel(y2_label, color=color)
        ax2.plot(self.dataframe['Date'], self.dataframe[y2], color=color)
        ax2.tick_params(axis='y', labelcolor=color)

        self.dataframe['Season'] = self.dataframe['Date'].dt.month.map(lambda m:
                                               "Winter" if m in [1, 2, 3] else
                                               "Summer" if m in [7, 8, 9] else
                                               None)
        previous_season = None
        season_start = None

        for i, row in self.dataframe.iterrows():
            current_season = row["Season"]

            if current_season and current_season != previous_season:
                # If switching to a new season, mark start
                season_start = row["Date"]

            if previous_season and current_season != previous_season:
                ax1.axvspan(season_start, row["Date"], color=self.season_colors[previous_season], alpha=0.3)

            previous_season = current_season

        # Format x-axis for better readability
        ax1.xaxis.set_major_locator(mdates.YearLocator())  # Show ticks every year
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))  # Format as year

        plt.tight_layout()


    def _get_y_label_with_units(self) -> str:
        if self.variable == 'Water_Content':
            y_label = 'Rolling Mean Soil Moisture (mg/g)'
            self.colour = '#17becf'
        elif self.variable == 'Water_level_meters':
            y_label = 'Rolling Mean Water Level (m)'
            self.colour = '#1f77b4'
        else:
            y_label = self.variable
            self.colour = '#1613d5'
        return y_label

    def _get_y_label(self) -> str:
        if self.variable == 'Water_Content':
            y = 'Rolling Mean Water_Content'
        elif self.variable == 'Water_level_meters':
            y = 'Rolling Mean Water_level_meters'
        else:
            y = self.variable
        return y

    def graph_rolling_coherence_ground_data(self) -> None:
        y1_list = ['r2', 'r2', 'normalised_r2', 'normalised_r2']
        y2_list = ['normalised_gradient', 'normalised_precipitation', 'normalised_gradient', 'normalised_precipitation']
        y_label_list = self._get_y_label_list()
        y2_colours = ['mediumaquamarine', 'aqua', 'mediumaquamarine', 'aqua']
        for y1, y2, y_label, y2_colour in zip(y1_list, y2_list, y_label_list, y2_colours):
            if y2 in self.dataframe:
                if self.path_to_directory == None:
                    self._get_plot(y1, y2, y_label, y2_colour)
                    plt.show()
                else:
                    plt.ioff()
                    files_already_exist = []
                    full_file_path = f'{self.path_to_directory}/window_{y1}_{y2}_{self.n}_{self.timeframe}_{self.location}_{self.variable}.png'

                    if os.path.exists(full_file_path):
                        files_already_exist.append(full_file_path)
                    else:
                        self._get_plot(y1, y2, y_label, y2_colour)
                        plt.savefig(full_file_path)
                        plt.close()

    def _get_y_label_list(self) -> list:
        if self.variable == 'Water_level_meters':
            y_label_list = ['R2 and normalised gradient of coherence and water level',
                            'R2 of coherence and water level and normalised precipitation',
                            'Normalised R2 and normalised gradient of coherence and water level'
                            'Normalised R2 of coherence and water level and normalised precipitation']
            y_label_list = ['\n'.join(wrap(label, 50)) for label in y_label_list]
        elif self.variable == 'Water_Content':
            y_label_list = ['R2 and normalised gradient of coherence and water content',
                            'R2 of coherence and water content and normalised precipitation',
                            'Normalised R2 and normalised gradient of coherence and water content'
                            'Normalised R2 of coherence and water content and normalised precipitation']
            y_label_list = ['\n'.join(wrap(label, 50)) for label in y_label_list]
        else:
            print("Neither Water_level_meters or Water_Content variables are defined")
            y_label_list = []
        return y_label_list

    def _get_plot(self, y1, y2, y_label: str, y2_colour: str) -> None:
        # Plotting
        plt.plot(self.dataframe['Date'], self.dataframe[y1], label=y1, color='teal')
        plt.plot(self.dataframe['Date'], self.dataframe[y2], label=y2, color=y2_colour)

        # Adding labels and legend
        plt.xlabel('Date')
        plt.ylabel(y_label)
        plt.tight_layout()
        plt.legend()
