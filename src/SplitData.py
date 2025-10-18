import pandas as pd


def focus_data(dataframe: pd.DataFrame, start_date:str, end_date:str) -> pd.DataFrame:
    dataframe = _ensure_data_time(dataframe)
    return dataframe[(dataframe['Date'] >= start_date) & (dataframe['Date'] <= end_date)]

def split_months_for_each_year(dataframe: pd.DataFrame) -> dict:
    dataframe = _ensure_data_time(dataframe)
    dataframe['Year'] = dataframe['Date'].dt.year
    year_month_data = {}
    for year in dataframe['Year'].unique():
        focused_dataframe = dataframe[dataframe['Year'] == year]
        year_month_data[year] = split_months(focused_dataframe)
    return year_month_data

def split_months(dataframe: pd.DataFrame)->dict:
    dataframe = _ensure_data_time(dataframe)
    return{
    'january': _season_split(dataframe, [1]),
        'february': _season_split(dataframe, [2]),
        'march': _season_split(dataframe, [3]),
        'april': _season_split(dataframe, [4]),
        'may': _season_split(dataframe, [5]),
        'june': _season_split(dataframe, [6]),
        'july': _season_split(dataframe, [7]),
        'august': _season_split(dataframe, [8]),
        'september': _season_split(dataframe, [9]),
        'october': _season_split(dataframe, [10]),
        'november': _season_split(dataframe, [11]),
        'december': _season_split(dataframe, [12]),
    }

def split_seasons(dataframe: pd.DataFrame)->dict:
    dataframe = _ensure_data_time(dataframe)
    winter_df = _season_split(dataframe, [1, 2, 3])
    spring_df = _season_split(dataframe, [4, 5, 6])
    summer_df = _season_split(dataframe, [7, 8, 9])
    autumn_df = _season_split(dataframe, [10, 11, 12])
    return {
        'winter': winter_df,
        'spring': spring_df,
        'summer': summer_df,
        'autumn': autumn_df
    }

def split_warm_cooler(dataframe: pd.DataFrame):
    dataframe = _ensure_data_time(dataframe)
    warmer_months = _season_split(dataframe, [4, 5, 6, 7, 8, 9])
    cooler_months = _season_split(dataframe, [1, 2, 3, 10, 11, 12])
    return {
        'warmer_months': warmer_months,
        'cooler_months': cooler_months
    }


def _season_split(dataframe:pd.DataFrame, months:[]):
    return dataframe[dataframe['Date'].dt.month.isin(months)]

def _ensure_data_time(dataframe: pd.DataFrame):
    dataframe['Date'] = pd.to_datetime(dataframe['Date'], format='%d/%m/%Y')
    return dataframe