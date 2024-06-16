"""BaseModelGui: adds a GUI to a pydantic model

Usage example
=============

**Register the BaseModel**

_Either with the decorator `@fl.base_model_with_gui_registration()`:_

    import fiatlight as fl
    from pydantic import BaseModel

    @fl.base_model_with_gui_registration(x__range=(0, 10))
    class MyParam(BaseModel):
        image_in: ImagePath
        x: int | None = None

_Or with `register_base_model`:_

    from pydantic import BaseModel

    class MyParam(BaseModel):
        image_in: ImagePath
        x: int | None = None

    from fiatlight.fiat_togui import register_base_model
    register_base_model(MyParam, x__range=(0, 10))

**Use the model in a function:**

    def f(param: MyParam) -> MyParam:
        return param

    fiatlight.run(f)
"""

from .dataclass_gui import DataclassLikeGui, DataclassLikeType
from fiatlight.fiat_types.error_types import Error, Unspecified, InvalidValue, ErrorValue
from fiatlight.fiat_types.base_types import JsonDict, FiatAttributes
from fiatlight.fiat_core import FiatToGuiException
from typing import Type
from pydantic import BaseModel, ValidationError


class BaseModelGui(DataclassLikeGui[DataclassLikeType]):
    """A sophisticated GUI for a pydantic model.
    Can edit and present all members of the model. Can handle nested models.
    Can catch validation errors and propagate them to the corresponding fields.
    """

    def __init__(self, basemodel_type: Type[DataclassLikeType], param_attrs: FiatAttributes | None = None) -> None:
        if not issubclass(basemodel_type, BaseModel):
            raise FiatToGuiException(f"{basemodel_type} is not a pydantic model")
        super().__init__(basemodel_type, param_attrs)  # type: ignore
        self.callbacks.load_from_dict = self._load_from_dict
        self.callbacks.save_to_dict = self._save_to_dict
        self.callbacks.clipboard_copy_possible = True
        self.callbacks.clipboard_copy_str = self.clipboard_copy_str

        # Look for fields with default_factory
        self._initialize_fields()

    def factor_dataclass_instance(self) -> DataclassLikeType | Error:
        try:
            instance = super().factor_dataclass_instance()
            if isinstance(instance, Error):
                raise RuntimeError(
                    f"""
                Internal error:
                ---------------
                BaseModelGui({self.datatype_name()}.factor_dataclass_instance()
                received an unexpected error: DataClassLikeGui.factor_dataclass_instance()
                should not return an error...
                """
                )
            return instance
        except ValidationError as e:
            validation_errors = e.errors()  # the detailed list of pydantic validation errors
            for validation_error in validation_errors:
                error_field_name_tuple = validation_error["loc"]  # a tuple of field name
                assert isinstance(error_field_name_tuple, tuple)
                assert isinstance(error_field_name_tuple, tuple)
                error_msg = validation_error["msg"]
                error_input = validation_error["input"]
                error_field_names = [error_field_name_tuple[i] for i in range(len(error_field_name_tuple))]
                for field_name in error_field_names:
                    assert isinstance(field_name, str)
                    if not self.has_param_of_name(field_name):
                        raise e
                    param = self.param_of_name(field_name)
                    if isinstance(param.data_with_gui.value, InvalidValue):
                        if param.data_with_gui.value.invalid_value != error_input:
                            new_attribute_exception = AttributeError(
                                f"""
                                Got twice a pydantic validation error with different values
                                for field {field_name} in class {self.datatype_name()}
                                """
                            )
                            raise new_attribute_exception from e
                        param.data_with_gui.value.error_message += " - " + error_msg
                    elif isinstance(param.data_with_gui.value, (Error, Unspecified)):
                        new_attribute_exception = AttributeError(
                            f"""
                                Internal fiatlight error. The field type should be DataType or InvalidValue,
                                not (Error, Unspecified)
                                for field {field_name} in class {self.datatype_name()}
                                """
                        )
                        raise new_attribute_exception from e
                    else:
                        param.data_with_gui.value = InvalidValue(invalid_value=error_input, error_message=error_msg)
            return ErrorValue

    def _initialize_fields(self) -> None:
        basemodel_type = self._type
        assert issubclass(basemodel_type, BaseModel)
        for field_name, model_field in basemodel_type.model_fields.items():
            param = self.param_of_name(field_name)
            if model_field.default_factory:
                param.default_value = model_field.default_factory()
                param.data_with_gui.callbacks.default_value_provider = model_field.default_factory

    @staticmethod
    def _save_to_dict(value: DataclassLikeType) -> JsonDict:
        r = {"type": "Pydantic", "value": value.model_dump(mode="json")}  # type: ignore
        return r

    def _load_from_dict(self, json_data: JsonDict) -> DataclassLikeType:
        json_data_type = json_data.get("type")
        if json_data_type != "Pydantic":
            raise ValueError(f"Expected type Pydantic, got {json_data_type}")
        assert self._type is not None
        assert issubclass(self._type, BaseModel)
        r = self._type.model_validate(json_data["value"])
        assert isinstance(r, self._type)
        return r  # type: ignore

    def clipboard_copy_str(self, value: DataclassLikeType) -> str:
        assert isinstance(value, BaseModel)
        return value.model_dump_json(indent=2)
