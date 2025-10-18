import pandas as pd

class GetSummaryMetrics:
    def __init__(self, dataframes: dict, column_of_focus:str='Coherence'):
        self.dataframe_names = list(dataframes.keys())
        self.dataframes = list(dataframes.values())
        self.column_of_focus = column_of_focus

    def run(self):
        if self._check_dataframes_have_same_dates():
            self.dataframes = self._check_consistent_column_names()
            summary_dataframe = pd.DataFrame({
                'Site': self.dataframe_names,
                f'Mean {self.column_of_focus}': self._get_mean_coherence_value(),
                f'Median {self.column_of_focus}': self._get_median_coherence_value(),
                f'Standard Deviation {self.column_of_focus}': self._get_standard_deviation_coherence_value(),
                f'Maximum {self.column_of_focus}': self._get_max_coherence_value(),
                f'Minimum {self.column_of_focus}': self._get_min_coherence_value()
            })
            return summary_dataframe
        else:
            print('The dates do not match across the dataframes')
            self.dataframes = self._check_consistent_column_names()
            summary_dataframe = pd.DataFrame({
                'Site': self.dataframe_names,
                f'Mean {self.column_of_focus}': self._get_mean_coherence_value(),
                f'Median {self.column_of_focus}': self._get_median_coherence_value(),
                f'Standard Deviation {self.column_of_focus}': self._get_standard_deviation_coherence_value(),
                f'Maximum {self.column_of_focus}': self._get_max_coherence_value(),
                f'Minimum {self.column_of_focus}': self._get_min_coherence_value()
            })
            return summary_dataframe

    def _get_standard_deviation_coherence_value(self):
        return [df[self.column_of_focus].std() for df in self.dataframes]

    def _get_median_coherence_value(self):
        return [df[self.column_of_focus].median() for df in self.dataframes]

    def _get_mean_coherence_value(self):
        return [df[self.column_of_focus].mean() for df in self.dataframes]

    def _get_min_coherence_value(self):
        return [df[self.column_of_focus].min() for df in self.dataframes]

    def _get_max_coherence_value(self):
        return [df[self.column_of_focus].max() for df in self.dataframes]

    def _check_dataframes_have_same_dates(self):
        first_dates = set(self.dataframes[0]["Date"])
        return all(set(dataframe["Date"]) == first_dates for dataframe in self.dataframes[1:])

    def _check_consistent_column_names(self):
        return [
            df.rename(columns={'mean': self.column_of_focus}) if self.column_of_focus not in df.columns and 'mean' in df.columns else df
            for df in self.dataframes]