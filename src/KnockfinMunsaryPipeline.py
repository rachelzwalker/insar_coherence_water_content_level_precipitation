import pandas as pd
from matplotlib import pyplot as plt

from CoherencePrecipitationGraphs import CoherencePrecipitationGraphs
from CorrelationRelationships import DataRelationships
from GeoDataFrameLocationCoherence import GeoDataframeLocationCoherence
from GetCoherenceGraphsDataDictionary import GetCoherenceGraphsDataDictionary
from MovingWindow import MovingWindow, GetRollingMean
from MovingWindowGraphs import MovingWindowLineGraphs, Variable, MovingWindowScatterGraphs
from Outputs import CoherenceGroundLineGraphs
from GetRollingPrecipitationDataframe import WindowTimeframe


def change_temperature_based_on_altitude(wick_dataframe, degrees_change, wick_weather_dataframe):
    wick_dataframe['tavg_updated'] = wick_weather_dataframe['tavg'] - degrees_change
    return wick_dataframe


def get_data_dictionaries(locations, site, subsites, dates_to_remove, root_directory, ground_data_path,
                          path_to_save_directory, reference_date_time, reference_date, points_path):
    dictionary_of_data_dictionaries = {}
    for location, subsite in zip(locations, subsites):
        data_dictionary = GetCoherenceGraphsDataDictionary(path=root_directory, ground_data_path=ground_data_path,
                                                           path_to_save_directory=path_to_save_directory,
                                                           location=location, reference_date_time=reference_date_time,
                                                           reference_date=reference_date, site=site, subsite=subsite,
                                                           path_to_points=points_path, input_data='point',
                                                           series_data_to_remove=dates_to_remove).run_method()
        dictionary_of_data_dictionaries[f'{location}'] = data_dictionary
        dataframe = dictionary_of_data_dictionaries[location]['coherence_ground_dataframe']
        dataframe.to_csv(f'{path_to_save_directory}/{location}.csv', index=True)
    return dictionary_of_data_dictionaries


def get_coherence_line_graphs(dictionary_for_site, path_to_save_directory):
    for site, dataframes in dictionary_for_site.items():
        CoherenceGroundLineGraphs(merged_dataframe=dataframes['coherence_ground_dataframe'],
                                  ground_data_variable=['Water_Content', 'Water_level_meters'], location=site,
                                  path_to_directory=path_to_save_directory,
                                  variable_name=['water content', 'water level (m)']).graph_coherence_ground_data()


def get_coherence_precipitation_outputs_wick_data(sites, weather_data_to_remove, root_directory_spring, points_path,
                                                  path_to_save_directory, one_month_rolling_precipitation,
                                                  six_week_rolling_precipitation, two_month_rolling_precipitation):
    for site in sites:
        dataframe = GeoDataframeLocationCoherence(path=root_directory_spring, location=site, path_to_points=points_path,
                                                  input_data='point',
                                                  data_series_dates_to_remove=weather_data_to_remove).dataframe_coherence()
        dataframe['Date'] = dataframe.index

        rolling_means_dataframes = GetRollingMean(None).rolling_means_with_window(dataframe)

        rolling_means_one_month = rolling_means_dataframes['one_month_rolling_mean_coherence'].rename_axis('time')
        rolling_means_six_weeks = rolling_means_dataframes['six_week_rolling_mean_coherence'].rename_axis('time')
        rolling_means_two_months = rolling_means_dataframes['two_month_rolling_mean_coherence'].rename_axis('time')

        rolling_means_one_month = rolling_means_one_month.sort_values(by='Date')
        rolling_means_six_weeks = rolling_means_six_weeks.sort_values(by='Date')
        rolling_means_two_months = rolling_means_two_months.sort_values(by='Date')

        CoherencePrecipitationGraphs(rolling_means_one_month, one_month_rolling_precipitation, path_to_save_directory,
                                     site,
                                     '1_month').rolling_mean_graph()

        CoherencePrecipitationGraphs(rolling_means_six_weeks, six_week_rolling_precipitation, path_to_save_directory,
                                     site,
                                     '6_weeks').rolling_mean_graph()

        CoherencePrecipitationGraphs(rolling_means_two_months, two_month_rolling_precipitation, path_to_save_directory,
                                     site,
                                     '2_months').rolling_mean_graph()

        DataRelationships(rolling_means_one_month, one_month_rolling_precipitation, max_lag=-50,
                          save_file_path=path_to_save_directory, site_name=site,
                          time_scale='1_month').get_relationships()

        DataRelationships(rolling_means_six_weeks, six_week_rolling_precipitation, max_lag=-50,
                          save_file_path=path_to_save_directory, site_name=site,
                          time_scale='6_week').get_relationships()

        DataRelationships(rolling_means_two_months, two_month_rolling_precipitation, max_lag=-50,
                          save_file_path=path_to_save_directory, site_name=site,
                          time_scale='2_months').get_relationships()

def plot_weather_conditions(weather_dataframe, site, path_to_save_directory):
    # Plotting using Matplotlib
    fig, ax1 = plt.subplots()

    # Create scatter plot
    ax1.scatter(weather_dataframe['Time'], weather_dataframe['Temp_Soil'], color='red', label='Soil Temperature',
                s=10)

    # Create bar plot on the same axes
    ax2 = ax1.twinx()
    ax2.bar(weather_dataframe['Time'], weather_dataframe['Precipitation_mm'], color='tab:blue',
            edgecolor='tab:blue', alpha=0.5, width=0.4,
            label='Daily precipitation')

    # Set labels and legends
    ax1.set_xlabel('Time')
    ax1.set_ylabel('Soil Temperature', color='black')
    ax2.set_ylabel('Precipitation (mm)', color='black')

    # Display legend
    lines, labels = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines + lines2, labels + labels2, loc='best')

    plt.savefig(f'{path_to_save_directory}/temp_ppt_{site}.png')
    plt.close()

class GetOutcomes:
    def __init__(self, path_to_save_directory, dictionary_of_data, precipitation_dataframe):
        self.path_to_save_directory = path_to_save_directory
        self.dictionary_of_data = dictionary_of_data
        self.precipitation_dataframe = precipitation_dataframe

    def get_outcomes(self):
        for site in self.dictionary_of_data.keys():
            dataframe = self.dictionary_of_data[site]['coherence_ground_dataframe']
            dataframe.dropna(how='any', inplace=True)

            subsite_name = site.lower().replace(' ', '_')

            try:
                moving_windows_water_content = MovingWindow(dataframe,
                                                            subsite_name,
                                                            self.precipitation_dataframe,
                                                            Variable.WATER_CONTENT,
                                                            save_filepath=self.path_to_save_directory).get_moving_window()

                self._get_windows_graphs(subsite_name, moving_windows_water_content, variable=Variable.WATER_CONTENT)

                self._get_lags(moving_windows_water_content, subsite_name, 'Rolling Mean Water_Content',
                               'water content')

            except:
                print(f'No water content data for {site}')

            try:
                moving_windows_water_level = MovingWindow(dataframe,
                                                          subsite_name,
                                                          self.precipitation_dataframe,
                                                          Variable.WATER_LEVEL,
                                                          save_filepath=self.path_to_save_directory).get_moving_window()

                self._get_windows_graphs(subsite_name, moving_windows_water_level, variable=Variable.WATER_LEVEL)

                self._get_lags(moving_windows_water_level, subsite_name, 'Rolling Mean Water_level_meters',
                               'water level')

            except:
                print(f'No water level data for {site}')

    def _get_lags(self, dictionary, site_name, variable='Rolling Mean Water_level_meters', variable_name='water level'):
        DataRelationships(dictionary['one_month_window'], dictionary['one_month_window'],
                          second_variable='Rolling Mean Precipitation_mm',
                          second_variable_name='precipitation',
                          max_lag=-50, save_file_path=self.path_to_save_directory, site_name=site_name,
                          time_scale='1_month').get_relationships()
        DataRelationships(dictionary['one_month_window'], dictionary['one_month_window'],
                          second_variable=variable,
                          second_variable_name=variable_name,
                          max_lag=-50, save_file_path=self.path_to_save_directory, site_name=site_name,
                          time_scale='1_month').get_relationships()
        DataRelationships(dictionary['six_week_window'], dictionary['six_week_window'],
                          second_variable='Rolling Mean Precipitation_mm',
                          second_variable_name='precipitation',
                          max_lag=-50, save_file_path=self.path_to_save_directory, site_name=site_name,
                          time_scale='6_week').get_relationships()
        DataRelationships(dictionary['six_week_window'], dictionary['six_week_window'],
                          second_variable=variable,
                          second_variable_name=variable_name,
                          max_lag=-50, save_file_path=self.path_to_save_directory, site_name=site_name,
                          time_scale='6_week').get_relationships()
        DataRelationships(dictionary['two_month_window'], dictionary['two_month_window'],
                          second_variable='Rolling Mean Precipitation_mm',
                          second_variable_name='precipitation',
                          max_lag=-50, save_file_path=self.path_to_save_directory, site_name=site_name,
                          time_scale='2_month').get_relationships()
        DataRelationships(dictionary['two_month_window'], dictionary['two_month_window'],
                          second_variable=variable,
                          second_variable_name=variable_name,
                          max_lag=-50, save_file_path=self.path_to_save_directory, site_name=site_name,
                          time_scale='2_month').get_relationships()

    def _get_windows_graphs(self, subsite_name, dictionary_windows, variable=Variable.WATER_CONTENT):
        MovingWindowLineGraphs(dictionary_windows['one_month_window'], variable, subsite_name,
                               WindowTimeframe.MONTH, path_to_directory=self.path_to_save_directory,
                               n=1).graphs_line()
        MovingWindowScatterGraphs(dictionary_windows['one_month_window'], variable, subsite_name,
                                  WindowTimeframe.MONTH, path_to_directory=self.path_to_save_directory,
                                  n=1).graph_scatter()
        MovingWindowLineGraphs(dictionary_windows['two_month_window'], variable, subsite_name,
                               WindowTimeframe.MONTH, path_to_directory=self.path_to_save_directory,
                               n=2).graphs_line()
        MovingWindowScatterGraphs(dictionary_windows['two_month_window'], variable, subsite_name,
                                  WindowTimeframe.MONTH, path_to_directory=self.path_to_save_directory,
                                  n=2).graph_scatter()
        MovingWindowLineGraphs(dictionary_windows['six_week_window'], variable, subsite_name,
                               WindowTimeframe.WEEK, path_to_directory=self.path_to_save_directory,
                               n=6).graphs_line()
        MovingWindowScatterGraphs(dictionary_windows['six_week_window'], variable, subsite_name,
                                  WindowTimeframe.WEEK, path_to_directory=self.path_to_save_directory,
                                  n=6).graph_scatter()


class GetMeansStandardDeviation:
    def __init__(self, dataframe, sites, variable, variable_name, test_name='Pearson'):
        self.dataframe = dataframe
        self.sites = sites
        self.variable = variable
        self.variable_name = variable_name
        self.test_name = test_name

    def get_means(self):
        dataframe_subset = self.dataframe[self.dataframe['site'].isin(self.sites)]
        dataframe_subset = dataframe_subset[dataframe_subset['variables'] == self.variable]
        dataframe_subset['window'] = dataframe_subset['window'].replace('2 months', '2_month')

        summary_dataframe = self.__get_summary_dataframe(dataframe_subset, 'overall')

        windows = ['2_month', '6_week', '1_month']
        for window in windows:
            time_subset = dataframe_subset[dataframe_subset['window'] == window]
            intermediate_dataframe = self.__get_summary_dataframe(time_subset, window)
            summary_dataframe = pd.concat([summary_dataframe, intermediate_dataframe])
        return summary_dataframe

    def __get_summary_dataframe(self, dataframe, window):
        mean = dataframe[self.test_name].mean()
        standard_deviation = dataframe[self.test_name].std()
        maximum = dataframe[self.test_name].max()
        minimum = dataframe[self.test_name].min()

        subsite_with_max = self.__get_maximum_or_minimum_subsite(dataframe, maximum)
        subsite_with_min = self.__get_maximum_or_minimum_subsite(dataframe, minimum)

        return pd.DataFrame({'Variable': self.variable_name, 'Time_frame': [window], f'Mean_{self.test_name}': [mean],
                             f'Standard_Deviation_{self.test_name}': standard_deviation,
                             f'Maximum_{self.test_name}': f'{maximum}: {subsite_with_max}',
                             f'Minimum_{self.test_name}': f'{minimum}: {subsite_with_min}'})

    def __get_maximum_or_minimum_subsite(self, dataframe, maximum_or_minimum):
        mask = dataframe[self.test_name] == maximum_or_minimum
        if mask.any():
            return dataframe.loc[mask, 'site'].values[0]
        return None


