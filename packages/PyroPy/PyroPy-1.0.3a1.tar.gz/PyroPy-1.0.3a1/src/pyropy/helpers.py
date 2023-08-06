"""Utility scripts for fire behaviour analysis."""
from datetime import datetime, timedelta
import numpy as np
import os
import warnings
from openpyxl import Workbook, load_workbook
from pandas import DataFrame

# if  __name__ == '__main__':
#     from firebehaviour import Incident
# else:
#     from .firebehaviour import Incident

def check_filepath(fn: str, suffix: str = None) -> bool:
    valid = os.path.isfile(fn)
    if not valid: warnings.warn(f'{fn} is not a valid filename')
    if suffix:
        fn = fn.split('.')
        valid = (fn[-1] == suffix)
        if not valid: warnings.warn(f'file must be a *.{suffix} file')
    return valid

def check_encoding(fn: str) -> str:
    """Returns the encoding of a csv file.
    
    TODO if encoding is Windws cp1252 change to latin-1 for better mapping see 
    http://python-notes.curiousefficiency.org/en/latest/python3/text_file_processing.html
    """
    with open(fn) as f:
        return(f.encoding)

def trim_by_datetimes(df: DataFrame, start: datetime, end: datetime) -> DataFrame:
    """Trims a dataframe to a specified time period.

    the dataframe must have at datetime field called `'date_time'`
    """
    return df[(df['date_time'] >= start) & (df['date_time'] <= end)]

def thin_by_timestep(df: DataFrame, time_step: float = 1) -> DataFrame:
    """Thins a dataframe by selecting rows based on a minumum time step.
    
    Args:
        timestep: hours
    """
    time_step = timedelta(hours=time_step)
    selected_rows_idx = []
    last_datetime = None
    for index, row in df.iterrows():
        if not last_datetime:
            last_datetime = row['date_time']
            selected_rows_idx.append(index)
        else:
            if row['date_time'] - last_datetime >= time_step:
                selected_rows_idx.append(index)
                last_datetime = row['date_time']

    return df.iloc[selected_rows_idx]

def adjust_precision(df: DataFrame, precision_dict: dict) -> DataFrame:
    """Rounds values to number of places specified in precision_dict.
    
    example precision dictionary
    precision_dict = {
        0: ['ffdi','fros', 'ros'],
        1: ['mc', 'mf'],
        2: []
    }
    """

    for precision, fields in precision_dict.items():
        for field in fields:
            try:
                df[field] = np.round(df[field],precision)
                if not precision: #don't store as float unnecessarily
                    df[field] = df[field].astype(int)
            except KeyError:
                pass # I know this is bad but do you have a better suggestion?
            except Exception as e:
                print(f'adjust precision error {type(e)}: {e}')

    return df





if __name__ == '__main__':
    pass
