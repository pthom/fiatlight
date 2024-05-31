from pydantic import BaseModel


class MydataPresenterParams(BaseModel):
    width: int = 100


class MydataPresenter:
    # class responsible for presenting a DataFrame as table,
    # with resizing columns, etc.
    params: MydataPresenterParams

    def __init__(self) -> None:
        self.params = MydataPresenterParams()
