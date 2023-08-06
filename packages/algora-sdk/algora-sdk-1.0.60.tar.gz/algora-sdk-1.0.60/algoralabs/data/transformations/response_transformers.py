import pandas as pd
from pandas import DataFrame


def no_transform(data: dict):
    return data


def to_pandas_with_index(data: dict, index: str = 'date') -> DataFrame:
    return pd.DataFrame(data).set_index(index)
