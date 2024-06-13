from pydantic import BaseModel
from fiatlight.fiat_core.possible_fiat_attributes import PossibleFiatAttributes


class MydataPossibleFiatAttributes(PossibleFiatAttributes):
    # Here we will add all the possible custom attributes for presentation and other options.
    def __init__(self) -> None:
        super().__init__("DataFrameWithGui")


_MYDATA_POSSIBLE_CUSTOM_ATTRIBUTES = MydataPossibleFiatAttributes()


class MydataPresenterParams(BaseModel):
    width: int = 100


class MydataPresenter:
    # class responsible for presenting a DataFrame as table,
    # with resizing columns, etc.
    params: MydataPresenterParams

    def __init__(self) -> None:
        self.params = MydataPresenterParams()

    @staticmethod
    def possible_custom_attributes() -> MydataPossibleFiatAttributes:
        return _MYDATA_POSSIBLE_CUSTOM_ATTRIBUTES
