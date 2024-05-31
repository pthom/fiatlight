import fiatlight as fl
import pandas as pd


def f(dataframe: pd.DataFrame) -> pd.DataFrame:
    return dataframe


fl.fiat_run(f)
