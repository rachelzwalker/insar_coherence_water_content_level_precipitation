import os

import pandas as pd
from matplotlib import pyplot as plt


class CoherencePrecipitationGraphs:
    def __init__(self, coherence_dataframe: pd.DataFrame,
                 precipitation_dataframe: pd.DataFrame,
                 save_path:str|None=None,
                 site:str='knockfin_a',
                 timescale:str='1_month',
                 additional_variable=None,
                 additional_psm_dataframe=None):
        self.coherence_dataframe = coherence_dataframe
        self.precipitation_dataframe = precipitation_dataframe
        self.save_path = save_path
        self.site = site
        self.timescale = timescale
        self.additional_variable = additional_variable
        self.psm_dataframe = additional_psm_dataframe

        self.color1 = 'navy'
        self.color2 = 'deepskyblue'
        self.color3 = 'green'

    def rolling_mean_graph(self):
        if self.additional_variable == None:
            self._rolling_mean_graph_two_axes()
        else:
            self._rolling_mean_graph_three_axes()

    def _rolling_mean_graph_three_axes(self) -> None:
        if self.save_path == None:
            self.get_graph_three_y_axes()
            plt.show()
        else:
            plt.ioff()
            files_already_exist = []
            full_file_path = f'{self.save_path}/overall_coherence_precipitation_{self.site}_{self.timescale}.png'

            if os.path.exists(full_file_path):
                files_already_exist.append(full_file_path)
            else:
                self.get_graph_three_y_axes()
                plt.savefig(full_file_path)
                plt.close()

    def _rolling_mean_graph_two_axes(self) -> None:
        if self.save_path == None:
            self._get_graph_two_y_axes()
            plt.show()
        else:
            plt.ioff()
            files_already_exist = []
            full_file_path = f'{self.save_path}/overall_coherence_precipitation_{self.site}_{self.timescale}.png'

            if os.path.exists(full_file_path):
                files_already_exist.append(full_file_path)
            else:
                self._get_graph_two_y_axes()
                plt.savefig(full_file_path)
                plt.close()

    def _get_graph_two_y_axes(self) -> None:
        fig, ax = plt.subplots()
        fig.subplots_adjust(right=0.75)

        twin1 = ax.twinx()

        p1, = ax.plot(self.coherence_dataframe['Date'], self.coherence_dataframe['Rolling Mean Coherence'], self.color1,
                      label="Coherence")
        p2, = twin1.plot(self.precipitation_dataframe['Date'],
                         self.precipitation_dataframe['Rolling Mean Precipitation'], self.color2, label="Precipitation")

        ax.set_xlabel("Date")
        ax.set_ylabel("Rolling Mean Coherence")
        twin1.set_ylabel("Rolling Mean Precipitation")

        ax.yaxis.label.set_color(self.color1)
        twin1.yaxis.label.set_color(self.color2)

        tkw = dict(size=4, width=1.5)
        ax.tick_params(axis='y', colors=self.color1, **tkw)
        twin1.tick_params(axis='y', colors=self.color2, **tkw)
        ax.tick_params(axis='x', **tkw)

        ax.legend(handles=[p1, p2])

    def get_graph_three_y_axes(self) -> None:
        fig, ax = plt.subplots()
        fig.subplots_adjust(right=0.75)

        twin1 = ax.twinx()
        twin2 = ax.twinx()

        twin2.spines.right.set_position(("axes", 1.2))

        p1, = ax.plot(self.coherence_dataframe['Date'], self.coherence_dataframe['Rolling Mean Coherence'], self.color1,
                      label="Coherence")
        p2, = twin1.plot(self.precipitation_dataframe['Date'],
                         self.precipitation_dataframe['Rolling Mean Precipitation'], self.color2,
                         label="Precipitation")
        p3, = twin2.plot(self.psm_dataframe['Date'], self.psm_dataframe[self.additional_variable], self.color3,
                         label="Amplitude")

        ax.set_xlabel("Date")
        ax.set_ylabel("Rolling Mean Coherence")
        twin1.set_ylabel("Rolling Mean Precipitation")
        twin2.set_ylabel(self.additional_variable)

        ax.yaxis.label.set_color(p1.get_color())
        twin1.yaxis.label.set_color(p2.get_color())
        twin2.yaxis.label.set_color(p3.get_color())

        tkw = dict(size=4, width=1.5)
        ax.tick_params(axis='y', colors=p1.get_color(), **tkw)
        twin1.tick_params(axis='y', colors=p2.get_color(), **tkw)
        twin2.tick_params(axis='y', colors=p3.get_color(), **tkw)
        ax.tick_params(axis='x', **tkw)

        ax.legend(handles=[p1, p2, p3])
