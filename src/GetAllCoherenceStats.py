from src.Pearson import Pearson
from src.PolynomialRegression import PolynomialRegression
from src.SplineGraphStats import Spline


class GetAllCoherenceStats:
    def __init__(self, location, path_to_directory=None, dataframes={}, variable='mean', variables_for_comparison=[],
                 degree_for_polynomical_regression=2):
        self.location = location
        self.path_to_directory = path_to_directory
        self.dataframes = dataframes
        self.variable = variable
        self.variables_for_comparison = variables_for_comparison
        self.degree = degree_for_polynomical_regression

    def get_stats(self):
        pearson_summary = Pearson(location=self.location, path_to_directory=self.path_to_directory,
                                  dataframes=self.dataframes, variable=self.variable,
                                  variables_for_comparison=self.variables_for_comparison).get_correlation_coefficient_and_p_value()
        polynomial_regression_summary = PolynomialRegression(location=self.location,
                                                             path_to_directory=self.path_to_directory,
                                                             dataframes=self.dataframes, variable=self.variable,
                                                             variables_for_comparison=self.variables_for_comparison,
                                                             degree=self.degree).get_stats_polynomial_regression()
        spline_summary = Spline(location=self.location, path_to_directory=self.path_to_directory,
                                dataframes=self.dataframes, variable=self.variable,
                                variables_for_comparison=self.variables_for_comparison).get_spline_stats()

        if self.path_to_directory is not None:
            pearson_summary.to_csv(f'{self.path_to_directory}/pearson_summary_{self.location}.csv')

        return {
            'pearson summary': pearson_summary,
            'polynomial regression': polynomial_regression_summary,
            'spline': spline_summary
        }

    def get_plots(self):
        PolynomialRegression(location=self.location, path_to_directory=self.path_to_directory,
                             dataframes=self.dataframes,
                             variable=self.variable,
                             variables_for_comparison=self.variables_for_comparison,
                             degree=self.degree).plot_polynomial_regression()
        Spline(location=self.location, path_to_directory=self.path_to_directory, dataframes=self.dataframes,
               variable=self.variable,
               variables_for_comparison=self.variables_for_comparison).plot_spline()
        Pearson(location=self.location, path_to_directory=self.path_to_directory, dataframes=self.dataframes,
                variable=self.variable,
                variables_for_comparison=self.variables_for_comparison).plot_pearson()
