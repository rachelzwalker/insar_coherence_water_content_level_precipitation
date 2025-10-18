import pandas as pd

from src.CoherenceGraph import CoherenceGraph
from src.GeoDataFrameLocationCoherence import GeoDataframeLocationCoherence
from src.GetDFGroundData import GetDFGroundData
from src.GroundDifferenceData import GroundDifferenceData
from src.Outputs import get_merged_dataframe, CoherenceGroundLineGraphs, CoherenceGroundScatterGraphs


class GetCoherenceGraphsDataDictionary:
    def __init__(self, path: str, ground_data_path: str, path_to_points: str | None = None,
                 path_to_save_directory: str | None = None, location: str = 'Knockfin A',
                 reference_date_time: str = '20180402T175024',
                 reference_date: str = '2018-04-02', site: str = 'KH',
                 subsite: str = 'A', input_data: str = 'polygon', buffer=None, series_data_to_remove=None):
        self.path = path
        self.path_to_directory = path_to_save_directory
        self.location = location
        self.reference_date_time = reference_date_time
        self.reference_date = reference_date
        self.ground_data_path = ground_data_path
        self.site = site
        self.subsite = subsite
        self.path_to_points = path_to_points
        self.input_data = input_data
        self.buffer = buffer
        self.series_data_to_remove = series_data_to_remove

        '''
        Input data can take the form of:
        - Polygon: In this case the coherence data should have been cropped using the GetUpToDateCroppedTifs. The path
        should be to the cropped coherence data. path_to_points and buffer should be None.
        - Point: In this case the path should be the list of tiffs (use the ListOfTiffs class) and path_to_points should
        be a path to the shapefiles. The raster pixel value will be collected. buffer should be None if want value of
        that pixel and a number if want buffer.

        '''

    def run_method(self) -> dict:
        dataframe = GeoDataframeLocationCoherence(path=self.path, location=self.location,
                                                  reference_date=self.reference_date_time,
                                                  path_to_points=self.path_to_points, input_data=self.input_data,
                                                  buffer=self.buffer,
                                                  data_series_dates_to_remove=self.series_data_to_remove).dataframe_coherence()
        dataframe = dataframe.sort_values(by=['Date'])

        dataframe = dataframe[dataframe['mean'] != 0.00] # added to remove any coherence mean values of 0 (means data not cover that area)


        CoherenceGraph(geodataframe=dataframe, location=self.location, input_data=self.input_data,
                       output_path=self.path_to_directory).graph()

        if self.input_data == 'polygon':
            mean_coherence = CoherenceGraph(geodataframe=dataframe, location=self.location,
                                            output_path=self.path_to_directory).mean_dataframe()
        else:
            mean_coherence = dataframe.drop(['geometry'], axis=1)


        temp_water = GetDFGroundData(data_path=self.ground_data_path, data_type='WT', site=self.site,
                                     subsite=self.subsite,
                                     variable='Temp_Water').get_variable_and_date_specific_csv()
        water_level = GetDFGroundData(data_path=self.ground_data_path, data_type='WT', site=self.site,
                                      subsite=self.subsite,
                                      variable='Water_level_meters').get_variable_and_date_specific_csv()
        temp_soil = GetDFGroundData(data_path=self.ground_data_path, data_type='Soil', site=self.site,
                                    subsite=self.subsite,
                                    variable='Temp_Soil').get_variable_and_date_specific_csv()
        water_content = GetDFGroundData(data_path=self.ground_data_path, data_type='Soil', site=self.site,
                                        subsite=self.subsite,
                                        variable='Water_Content').get_variable_and_date_specific_csv()

        temp_water_difference = self._get_difference(temp_water, variable='Temp_Water')
        water_level_difference = self._get_difference(water_level, 'Water_level_meters')
        temp_soil_difference = self._get_difference(temp_soil, 'Temp_Soil')
        water_content_difference = self._get_difference(water_content, 'Water_Content')


        try:
            coherence_ground_df, dataframes_not_empty = self._get_summary_dataframe(mean_coherence, temp_soil_difference,
                                                                                    temp_water_difference,
                                                                                    water_content_difference,
                                                                                    water_level_difference)


            ground_data_variables_raw = []
            ground_data_variables_difference = []
            variable_raw_names = []
            variable_difference_names = []

            ground_data_variables_raw_to_check = ['Temp_Water', 'Water_level_meters', 'Temp_Soil', 'Water_Content']
            ground_data_variables_difference_to_check = ['Difference_Temp_Water', 'Difference_Water_level_meters',
                                                         'Difference_Temp_Soil', 'Difference_Water_Content']
            variable_raw_names_to_check = ['Water Temperature', 'Water Level (m)', 'Soil Temperature', 'Water Content']
            variable_difference_names_to_check = ['Water Temperature Difference', 'Water Level Difference (m)',
                                                  'Soil Temperature Difference', 'Water Content Difference']

            # currently not graphing the data for polygons or points

            for item in dataframes_not_empty:
                for ground_variable_raw, ground_variable_difference, variable_raw_name, variable_difference_name in zip(
                        ground_data_variables_raw_to_check, ground_data_variables_difference_to_check,
                        variable_raw_names_to_check, variable_difference_names_to_check):
                    if ground_variable_raw in item.columns:
                        ground_data_variables_raw.append(ground_variable_raw)
                        ground_data_variables_difference.append(ground_variable_difference)
                        variable_raw_names.append(variable_raw_name)
                        variable_difference_names.append(variable_difference_name)


            for raw, difference, raw_name, difference_name in zip(ground_data_variables_raw,
                                                                  ground_data_variables_difference,
                                                                  variable_raw_names,
                                                                  variable_difference_names):

                CoherenceGroundLineGraphs(merged_dataframe=coherence_ground_df,
                                          ground_data_variable=[raw], location=self.location,
                                          path_to_directory=self.path_to_directory,
                                          variable_name=[raw_name]).graph_coherence_ground_data()
                CoherenceGroundScatterGraphs(merged_dataframe=coherence_ground_df,
                                             ground_data_variable=[raw], location=self.location,
                                             path_to_directory=self.path_to_directory,
                                             variable_name=[raw_name]).graph_scatter_coherence_ground()

                CoherenceGroundLineGraphs(merged_dataframe=coherence_ground_df,
                                          ground_data_variable=[difference], location=self.location,
                                          path_to_directory=self.path_to_directory,
                                          variable_name=[difference_name]).graph_coherence_ground_data()

            return {
                'coherence_dataframe': dataframe,
                'coherence_ground_dataframe': coherence_ground_df
            }
        except:
            print('No or not enough data overlap between coherence data and ground data')


    def _get_difference(self, dataframe: pd.DataFrame, variable: str) -> pd.DataFrame:
        # issue is if the data acquired does not cover the reference date.
        if not dataframe.empty:
            return GroundDifferenceData(ground_dataframe=dataframe, reference_date=self.reference_date,
                                        variable=variable).get_difference_data()
        else:
            return pd.DataFrame()

    def _get_summary_dataframe(self, mean_coherence: pd.DataFrame, temp_soil, temp_water, water_content, water_level):
        dataframes_not_empty = []

        if not temp_water.empty:
            temp_water_coherence_df = get_merged_dataframe(ground_dataframe=temp_water,
                                                           coherence_dataframe=mean_coherence)
            dataframes_not_empty.append(temp_water_coherence_df)
        else:
            temp_water_coherence_df = temp_water
        if not water_level.empty:
            water_level_coherence_df = get_merged_dataframe(ground_dataframe=water_level,
                                                            coherence_dataframe=mean_coherence)

            dataframes_not_empty.append(water_level_coherence_df)
        else:
            water_level_coherence_df = water_level
        if not temp_soil.empty:
            temp_soil_coherence_df = get_merged_dataframe(ground_dataframe=temp_soil,
                                                          coherence_dataframe=mean_coherence)
            dataframes_not_empty.append(temp_soil_coherence_df)
        else:
            temp_soil_coherence_df = temp_soil
        if not water_content.empty:
            water_content_coherence_df = get_merged_dataframe(ground_dataframe=water_content,
                                                              coherence_dataframe=mean_coherence)
            dataframes_not_empty.append(water_content_coherence_df)
        else:
            water_content_coherence_df = water_content

        dataframes_to_join_inc_empty = [temp_water_coherence_df, water_level_coherence_df, temp_soil_coherence_df,
                                        water_content_coherence_df]
        # dataframes_to_join = list(filter(lambda df: not df.empty, dataframes_to_join_inc_empty))

        self._remove_nan_from_each_df(dataframes_not_empty)

        coherence_ground_df_with_repeated_columns = self._combine_the_dataframes(dataframes_not_empty)
        coherence_ground_df = self._tidy_the_dataframe(coherence_ground_df_with_repeated_columns)
        return coherence_ground_df, dataframes_not_empty

    @staticmethod
    def _tidy_the_dataframe(coherence_ground_df_with_repeated_columns: pd.DataFrame) -> pd.DataFrame:
        coherence_ground_df = coherence_ground_df_with_repeated_columns.loc[:,
                              ~coherence_ground_df_with_repeated_columns.columns.duplicated()].copy()
        column_to_move = coherence_ground_df.pop('mean')
        coherence_ground_df.insert(0, 'mean', column_to_move)
        coherence_ground_df = coherence_ground_df.drop(columns=['Date'])
        return coherence_ground_df

    @staticmethod
    def _combine_the_dataframes(dataframes_to_join: list) -> pd.DataFrame:
        return pd.concat(dataframes_to_join, axis=1)

    @staticmethod
    def _remove_nan_from_each_df(dataframes_to_join: list) -> list:
        for dataframe in dataframes_to_join:
            dataframe.dropna(axis=1, how='all', inplace=True)
            dataframe.dropna(how='any', inplace=True)
        return dataframes_to_join
