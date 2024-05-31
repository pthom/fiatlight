import fiatlight as fl
import pandas as pd


def default_dataframe() -> pd.DataFrame:
    # Here, we provide an example data frame to the user,
    # using the Titanic dataset from the Data Science Dojo repository.
    # (widely used in data science tutorials)
    url = "https://raw.githubusercontent.com/datasciencedojo/datasets/master/titanic.csv"
    try:
        df = pd.read_csv(url)
    except Exception as e:
        print(f"Error loading sample dataset: {e}")
        df = pd.DataFrame()  # Return an empty DataFrame in case of failure
    return df


def f(dataframe: pd.DataFrame | None = None) -> pd.DataFrame:
    if dataframe is None:
        dataframe = default_dataframe()
    return dataframe


fl.fiat_run(f)
