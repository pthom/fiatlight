from pydantic import BaseModel
from fiatlight.fiat_core.possible_fiat_attributes import PossibleFiatAttributes


class MydataPossibleFiatAttributes(PossibleFiatAttributes):
    # Here we will add all the possible fiat attributes for presentation and other options.
    def __init__(self) -> None:
        super().__init__("DataFrameWithGui")

        self.add_explained_attribute(name="width", type_=int, default_value=100, explanation="Width of the table")


_MYDATA_POSSIBLE_FIAT_ATTRIBUTES = MydataPossibleFiatAttributes()


class MydataPresenterParams(BaseModel):
    # Parameters for the MydataPresenter
    width: int = 100


class MydataPresenter:
    # class responsible for presenting a DataFrame as table,
    # with resizing columns, etc.
    params: MydataPresenterParams

    def __init__(self) -> None:
        self.params = MydataPresenterParams()

    @staticmethod
    def possible_fiat_attributes() -> MydataPossibleFiatAttributes:
        return _MYDATA_POSSIBLE_FIAT_ATTRIBUTES
