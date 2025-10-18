import pandas as pd

class CoherenceGraph:
    def __init__(self, geodataframe, location, output_path, input_data='polygon'):
        self.geodataframe = geodataframe
        self.location = location
        self.input_data = input_data
        self.output_path = output_path

    def graph(self):
        if 'Lat' in self.geodataframe.columns:
            geodataframe = self.geodataframe[['geometry', 'mean']]
        else:
            geodataframe = self.geodataframe
        full_mean_gdf = self.mean_dataframe(geodataframe)
        mean_gdf = full_mean_gdf[['mean']]
        ax = mean_gdf.plot(rot=45, title=f'Mean coherence over time at {self.location}')
        ax.set_xlabel("Time")
        ax.set_ylabel("Coherence")
        fig = ax.get_figure()
        fig.savefig(f'{self.output_path}/mean_coherence_{self.location}.png')


    def mean_dataframe(self, geodataframe:pd.DataFrame) -> pd.DataFrame:
        dataframe = self._get_initial_dataframe(geodataframe)

        if self.input_data == 'polygon':
            mean_df = self._get_mean_dataframe(dataframe)
        else:
            mean_df = dataframe
        return mean_df

    def _get_mean_dataframe(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        dataframe = dataframe.loc[(dataframe != 0).any(axis=1)]
        dataframe_with_means = self._add_mean(dataframe)
        mean_df = dataframe_with_means['mean']
        mean_df = mean_df.rename_axis("Date")
        return pd.DataFrame(mean_df)

    def _get_initial_dataframe(self, geodataframe:pd.DataFrame) -> pd.DataFrame:
        if self.input_data == 'polygon':
            dataframe = self._transform_dataframe(geodataframe)
            dataframe['Date'] = dataframe.index
            dataframe['Date'] = pd.to_datetime(dataframe['Date'])
            dataframe = dataframe.set_index('Date')
        else:
            dataframe = geodataframe.drop(['geometry'], axis=1)
        return dataframe

    def _add_mean(self, geodataframe_to_graph:pd.DataFrame) -> pd.DataFrame:
        geodataframe_to_graph['mean'] = geodataframe_to_graph.mean(axis=1)
        return geodataframe_to_graph

    def _transform_dataframe(self, geodataframe: pd.DataFrame) -> pd.DataFrame:
        return geodataframe.T