from typing import Any, Generic, Optional
import logging
from fiatlight.fiat_types.base_types import DataType
from fiatlight.fiat_types.function_types import DataValidationFunction


def typename_to_type_secure(typename: str) -> Optional[type]:
    """Converts a type name string to a type. Only allows a few authorized types (int, float, str, bool)."""
    authorized_types = {
        "int": int,
        "float": float,
        "str": str,
        "bool": bool,
    }
    return authorized_types.get(typename, None)


def _permissive_is_instance(value: Any, type_: type) -> bool:
    """Checks if the value is an instance of the type, but allows float to be an instance of int."""
    if type_ == float and isinstance(value, int):
        return True
    return isinstance(value, type_)


def parse_tuple_definition(tuple_definition: str) -> Optional[tuple[type, ...]]:
    """Parses a tuple definition string, like "(int, int)"."""
    if not (tuple_definition.startswith("(") and tuple_definition.endswith(")")):
        return None
    type_strings = tuple_definition[1:-1].split(", ")
    types = tuple(typename_to_type_secure(ts) for ts in type_strings)
    has_unknown_types = any(t is None for t in types)

    if has_unknown_types:
        logging.error(f"parse_tuple_definition: unknown types in tuple definition: {tuple_definition}")
        return None
    else:
        return types  # type: ignore


class DetailedType(Generic[DataType]):
    """DetailedType: a type, with more details for tuple and list types.

    Attributes:
        type_: The type of the variable.
        type_details: Additional details for the type, or None for standard types.
    """

    type_: type[DataType]
    type_details: Optional[str]
    _tuple_detailed_types: Optional[tuple[type, ...]]
    _list_inner_type: Optional[type]

    def __init__(self, type_: type[DataType], type_details: Optional[str] = None) -> None:
        self.type_ = type_
        self.type_details = type_details
        self._tuple_detailed_types = None
        self._list_inner_type = None

        if type_details:
            if type_details.startswith("(") and type_details.endswith(")"):
                self._tuple_detailed_types = parse_tuple_definition(type_details)
            elif type_details.startswith("[") and type_details.endswith("]"):
                self._list_inner_type = typename_to_type_secure(type_details[1:-1])

            if self._tuple_detailed_types is None and self._list_inner_type is None:
                msg = f"""DetailedType: Invalid type details: {type_details}
                Should be a tuple like "(int, int)" or a list like "[int]".
                """
                logging.error(msg)
                raise ValueError(msg)

    def is_value_ok(self, value: Any) -> bool:
        """Checks if the given value is valid according to the type and details."""
        if not _permissive_is_instance(value, self.type_):
            return False
        if self.type_details is None:
            return True

        if self._tuple_detailed_types is not None:
            return self._check_if_value_matches_tuple_type(value)
        if self._list_inner_type is not None:
            return self._check_if_value_matches_list_type(value)
        raise ValueError(f"Invalid type details: {self.type_details}")

    def _check_if_value_matches_tuple_type(self, value: Any) -> bool:
        """Helper method to check tuple types."""
        if not isinstance(value, tuple) and not isinstance(value, list):
            return False
        assert self._tuple_detailed_types is not None
        if len(value) != len(self._tuple_detailed_types):
            return False
        return all(_permissive_is_instance(v, t) for v, t in zip(value, self._tuple_detailed_types))

    def _check_if_value_matches_list_type(self, value: Any) -> bool:
        """Helper method to check list types."""
        if not isinstance(value, tuple) and not isinstance(value, list):
            return False
        assert self._list_inner_type is not None
        return all(_permissive_is_instance(v, self._list_inner_type) for v in value)

    def type_str(self) -> str:
        """Returns a string representation of the type."""
        return self.type_.__name__ if self.type_details is None else self.type_details

    def __str__(self) -> str:
        return self.type_str()


class DetailedVar(Generic[DataType]):
    """DetailedVar: A variable with a name, detailed type, and additional explanation."""

    name: str
    type_: DetailedType[DataType]
    explanation: str
    data_validation_function: Optional[DataValidationFunction[DataType]]

    def __init__(
        self,
        name: str,
        type_: type[DataType],
        explanation: str,
        type_details: Optional[str] = None,
        data_validation_function: Optional[DataValidationFunction[DataType]] = None,
    ) -> None:
        self.name = name
        self.explanation = explanation
        self.type_ = DetailedType(type_, type_details)
        self.data_validation_function = data_validation_function

    def documentation(self, width_name_and_type: int) -> str:
        """Generates documentation for the variable."""
        name_and_type = f"{self.name} ({self.type_.type_str()})"
        name_and_type_padded = name_and_type.ljust(width_name_and_type)
        return f"{name_and_type_padded}: {self.explanation}"

    def is_value_ok(self, value: Any) -> bool:
        """Checks if the given value is valid."""
        if not self.type_.is_value_ok(value):
            return False
        if self.data_validation_function is not None:
            return self.data_validation_function(value)
        return True


class DetailedVarValue(Generic[DataType]):
    """DetailedVarValue: A variable with a value, including type and validation information."""

    detailed_var: DetailedVar[DataType]
    value: DataType

    def __init__(self, detailed_var: DetailedVar[DataType], value: DataType) -> None:
        self.detailed_var = detailed_var
        self.value = value

    def is_value_ok(self) -> bool:
        """Checks if the value is valid according to the variable's type and validation function."""
        return self.detailed_var.is_value_ok(self.value)
