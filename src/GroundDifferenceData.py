import pandas as pd

class GroundDifferenceData:
    def __init__(self, ground_dataframe: pd.DataFrame, reference_date:str, variable:str):
        self.ground_dataframe = ground_dataframe
        self.reference_date = reference_date
        self.variable = variable

    def get_difference_data(self) -> pd.DataFrame:
        try:
            value = self._get_reference_cell_value()
            self.ground_dataframe[f'Difference_{self.variable}'] = (self.ground_dataframe[self.variable] - value)/value
            return self.ground_dataframe
        except:
            print('The ground data does not include the reference date')
            return self.ground_dataframe

    def _get_reference_cell_value(self) -> pd.DataFrame:
        transposed_dataframe = self.ground_dataframe.T
        return transposed_dataframe.iloc[0][self.reference_date]
