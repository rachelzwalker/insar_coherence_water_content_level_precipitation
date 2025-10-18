import pandas as pd
from scipy.stats import linregress
import seaborn as sns
import matplotlib.pyplot as plt


class LagsAnalysis:
    def __init__(self, site_name, lags: pd.DataFrame, comparison: pd.DataFrame, comparison_variable: str):
        self.lags = lags
        self.comparison = comparison
        self.comparison_variable = comparison_variable
        self.site_name = site_name

    def run(self) -> dict:
        return {f'{self.site_name}_{self.comparison_variable}': {
            f'mean_{self.comparison_variable}': self._get_mean_comparison_variable(),
            f'max_{self.comparison_variable}': self._get_max_comparison_variable(),
            f'min_{self.comparison_variable}': self._get_min_comparison_variable(),
            'peak_lag': self._get_lag_peak(),
            'trough_lag': self._get_lag_trough()
        }
        }

    def _get_max_comparison_variable(self):
        return self.comparison[self.comparison_variable].max()

    def _get_min_comparison_variable(self):
        return self.comparison[self.comparison_variable].min()

    def _get_mean_comparison_variable(self):
        return self.comparison[self.comparison_variable].mean()

    def _get_lag_peak(self):
        return self.lags.loc[self.lags["cross_correlation_time"].idxmax(), "lags"]

    def _get_lag_trough(self):
        return self.lags.loc[self.lags["cross_correlation_time"].idxmin(), "lags"]


class LagsGraphs:
    def __init__(self, lags_dictionary: dict, output_path: str | None, filter_aspect: str = 'winter_Water',
                 peak_or_trough: str = 'Peak'):
        self.lags_dictionary = lags_dictionary
        self.output_path = output_path
        self.filter_aspect = filter_aspect
        self.peak_trough = peak_or_trough

    def run(self):
        dataframe = self._get_lags_dataframe()
        dataframe = dataframe[['site_name', 'lag_period', 'mean_Water_level_meters', 'peak_lag', 'trough_lag']]
        filtered_dataframe = self._get_filtered_dataframe(dataframe)
        unique_lag_periods = filtered_dataframe['lag_period'].unique()
        self._get_scatter_graph_for_each_time_period(unique_lag_periods, filtered_dataframe)

    def _get_scatter_graph_for_each_time_period(self, unique_lag_periods, filtered_dataframe):
        for lag in unique_lag_periods:
            subset = filtered_dataframe[filtered_dataframe['lag_period'] == lag]  # Filter data for this lag_period

            # Linear regression
            slope, intercept, r_value, _, _ = linregress(subset['peak_lag'], subset['mean_Water_level_meters'])
            r2 = r_value ** 2  # Compute R² value

            # Create the plot
            plt.figure(figsize=(6, 4))
            sns.regplot(data=subset, x=f'{self.peak_trough}_lag', y='mean_Water_level_meters', scatter=True, ci=None, color='blue',
                        line_kws={'color': 'red'})  # Regression line

            # Plot customization
            plt.title(f'Scatter Plot for {lag}')
            plt.xlabel(f'{self.peak_trough} Lag')
            plt.ylabel('Mean Water Level (m)')
            plt.grid(True)

            # Add R² value to the plot
            plt.text(
                max(subset[f'{self.peak_trough}_lag']) * 0.7,  # X position
                max(subset['mean_Water_level_meters']) * 0.9,  # Y position
                f'R² = {r2:.3f}', fontsize=12, color='red'
                # f'R = {r_value:.3f}', fontsize=12, color='red'
            )

            # Remove legend
            plt.legend([], [], frameon=False)
            if self.output_path is not None:
                plt.savefig(
                    f'{self.output_path}/{lag}_lag_correlation_{self.filter_aspect}_{self.peak_trough}.png')
            else:
                plt.show()

    def _get_filtered_dataframe(self, dataframe) -> pd.DataFrame:
        return dataframe[dataframe['site_name'].str.contains(self.filter_aspect, case=False, na=False)]

    def _get_lags_dataframe(self) -> pd.DataFrame:
        data = []
        for lag_key, records in self.lags_dictionary.items():
            for record in records:
                site_name, values = next(iter(record.items()))  # Extract site name and values
                values['site_name'] = site_name  # Add site name as a column
                values['lag_period'] = lag_key  # Add lag period
                data.append(values)
        return pd.DataFrame(data)
