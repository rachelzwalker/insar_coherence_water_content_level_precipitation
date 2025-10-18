import pandas as pd

from src.ListOfFiles import get_list_of_files

class GetDFGroundData:
    def __init__(self, data_path:str, data_type:str='WT', site:str='KH', subsite:str='A', variable:str='Temp_Water'):
        self.path = data_path
        self.data_type = data_type
        self.site = site
        self.subsite = subsite
        self.variable = variable

    def get_variable_and_date_specific_csv(self) -> pd.DataFrame:
        dataframe = self.create_dataframe_for_whole_csv()
        if dataframe.empty == False:
            if self.variable != 'Precipitation_mm':
                dataframe['Date'] = pd.to_datetime(dataframe['Date'], dayfirst=True, errors='coerce')
                mean_measurements = dataframe.groupby('Date')[self.variable].mean().reset_index()
                mean_measurements = mean_measurements.set_index('Date')
                return mean_measurements
            else:
                dataframe['Date'] = pd.to_datetime(dataframe['Date'], dayfirst=True, errors='coerce')
                sum_measurements = dataframe.groupby('Date')[self.variable].sum().reset_index()
                sum_measurements = sum_measurements.set_index('Date')
                return  sum_measurements
        else:
            return pd.DataFrame()


    def create_dataframe_for_whole_csv(self) -> pd.DataFrame:
        file = self._get_file()
        if file == []:
            print(f" The {self.data_type} file does not exist for the {self.site} {self.subsite} site")
            return pd.DataFrame()
        else:
            return pd.read_csv(file[0])


    def _get_file(self) -> list:
        list_of_files = get_list_of_files(self.path)
        files_containing_data_type = self._get_list_files_on_data_type(list_of_files)
        files_containing_sites = self._get_site_files(files_containing_data_type, self.site)
        return self._get_site_files(files_containing_sites, self.subsite)


    def _get_list_files_on_data_type(self, list_of_files:list) -> list:
        if self.data_type == 'WT':
            return [x for x in list_of_files if "WT" in x]
        else:
            return [x for x in list_of_files if not "WT" in x]


    @staticmethod
    def _get_site_files(list_of_reduced_files:list, site_subsite:str) -> list:
        return [x for x in list_of_reduced_files if site_subsite in x]


class RaiseVariableError:
    def __init__(self, variable:str, data_type:str):
        self.variable = variable
        self.data_type = data_type

    def raise_variable_error(self):
        if self.data_type == 'WT':
            print(
                f"The variable {self.variable} is not in the {self.data_type} dataframe, change the variable name to Temp_Water or Water_level_meters")
        else:
            print(
                f"The variable {self.variable} is not in the {self.data_type} dataframe, change the variable name to Temp_Soil or Water_Content")


