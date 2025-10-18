import os

import pandas as pd
from matplotlib import pyplot as plt


def get_merged_dataframe(ground_dataframe: pd.DataFrame, coherence_dataframe: pd.DataFrame) -> pd.DataFrame:
    merged_dataframe = pd.merge(ground_dataframe, coherence_dataframe, on='Date', how='left')
    merged_dataframe['Date'] = merged_dataframe.index
    return merged_dataframe


class CoherenceGroundScatterGraphs:
    def __init__(self, merged_dataframe: pd.DataFrame, ground_data_variable: list, location: str,
                 path_to_directory: None | str = None, variable_name: list = [],
                 figsize: tuple[int] = (10, 5)):
        self.location = location
        self.path_to_directory = path_to_directory
        self.merged_dataframe = merged_dataframe
        self.variable = ground_data_variable
        self.variable_name = variable_name
        self.figsize = figsize

    def graph_scatter_coherence_ground(self) -> None:
        if self.path_to_directory == None:
            self._get_plot()
        else:
            plt.ioff()
            files_already_exist = []
            if os.path.exists(f'{self.path_to_directory}/coherence_ground_scatter{self.location}_{self.variable}.png'):
                files_already_exist.append(
                    f'{self.path_to_directory}/coherence_ground_scatter{self.location}_{self.variable}.png')
            else:
                self._get_plot()
                plt.savefig(f'{self.path_to_directory}/coherence_ground_scatter{self.location}_{self.variable}.png')
                plt.close()

    def _get_plot(self) -> None:
        if 'Date' not in self.merged_dataframe:
            self.merged_dataframe['Date'] = self.merged_dataframe.index
        fig, ax = plt.subplots(figsize=self.figsize)
        if self.variable_name != []:
            for variable, variable_name in zip(self.variable, self.variable_name):
                if variable in self.merged_dataframe.columns:

                    if 'level' in self.variable_name:
                        colour = '#1f77b4'
                    elif 'soil' in self.variable or 'content' in self.variable_name:
                        colour = '#17becf'
                    else:
                        colour = '#1613d5'

                    ax.scatter(self.merged_dataframe['mean'], self.merged_dataframe[variable], color=colour)
                    plt.xlabel('Coherence')
                    plt.ylabel(variable_name)
                    plt.legend(labels=self.variable_name)
        else:
            for variable in self.variable:

                if 'level' in self.variable:
                    colour = '#1f77b4'
                    label = variable
                elif 'soil' in self.variable or 'content' in self.variable:
                    colour = '#17becf'
                    label = 'Soil Moisture (mg/g)'
                else:
                    colour = '#1613d5'
                    label = variable

                ax.scatter(self.merged_dataframe['mean'], self.merged_dataframe[variable], color=colour)
                plt.xlabel('Coherence')
                plt.ylabel(label)
                plt.legend(labels=self.variable)


class CoherenceGroundLineGraphs:
    def __init__(self, merged_dataframe: pd.DataFrame, ground_data_variable: list, location: str,
                 path_to_directory: str | None = None, variable_name: list = [],
                 figsize:tuple[int]=(10, 5)):
        self.location = location
        self.path_to_directory = path_to_directory
        self.merged_dataframe = merged_dataframe
        self.variable = ground_data_variable
        self.variable_name = variable_name
        self.figsize = figsize

    def graph_coherence_ground_data(self) -> None:
        if self.path_to_directory == None:
            self._get_plot()
        else:
            plt.ioff()
            files_already_exist = []
            if os.path.exists(f'{self.path_to_directory}/coherence_ground_line{self.location}_{self.variable}.png'):
                files_already_exist.append(
                    f'{self.path_to_directory}/coherence_ground_line{self.location}_{self.variable}.png')
            else:
                self._get_plot()
                plt.savefig(f'{self.path_to_directory}/coherence_ground_line{self.location}_{self.variable}.png')
                plt.close()

    def _get_plot(self) -> None:
        if 'Date' not in self.merged_dataframe:
            self.merged_dataframe['Date'] = self.merged_dataframe.index
        fig, ax = plt.subplots(figsize=self.figsize)
        if self.variable_name != None:
            for variable, variable_name in zip(self.variable, self.variable_name):
                if variable in self.merged_dataframe.columns:
                    self.merged_dataframe.plot(x='Date', y=variable, ax=ax, label=variable_name)
        else:
            for variable in self.variable:
                if variable in self.merged_dataframe.columns:
                    self.merged_dataframe.plot(x='Date', y=variable, ax=ax)
        self.merged_dataframe['mean'] = self.merged_dataframe['mean'].interpolate(method='linear')
        self.merged_dataframe.plot(x='Date', y='mean', ax=ax, secondary_y=True, label='Coherence')
