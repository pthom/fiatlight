from pydantic import BaseModel


class DataFramePresenterParams(BaseModel):
    width: int = 100


class DataFramePresenter:
    # class responsible for presenting a DataFrame as table,
    # with resizing columns, etc.
    params: DataFramePresenterParams

    def __init__(self) -> None:
        self.params = DataFramePresenterParams()
