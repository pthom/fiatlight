from typing import Any, Generic, Optional
import logging

from fiatlight.fiat_types import Unspecified, UnspecifiedValue
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
    tuple_types: Optional[tuple[type, ...]]
    list_inner_type: Optional[type]
    dict_types: Optional[tuple[type, type]]

    def __init__(
        self,
        type_: type[DataType],
        *,
        tuple_types: Optional[tuple[type, ...]] = None,
        list_inner_type: Optional[type] = None,
        dict_types: Optional[tuple[type, type]] = None,
    ) -> None:
        self.type_ = type_
        if tuple_types is not None and list_inner_type is not None:
            raise ValueError("DetailedType: cannot have both tuple_types and list_inner_type")
        if tuple_types is not None and type_ != tuple:
            raise ValueError("DetailedType: tuple_types can only be set for tuple types")
        if list_inner_type is not None and type_ != list:
            raise ValueError("DetailedType: list_inner_type can only be set for list types")
        self.tuple_types = tuple_types
        self.list_inner_type = list_inner_type
        self.dict_types = dict_types

    def is_value_type_ok(self, value: Any) -> bool:
        """Checks if the given value is valid according to the type and details."""
        if not _permissive_is_instance(value, self.type_):
            return False
        if self.tuple_types is not None:
            return self._check_if_value_matches_tuple_type(value)
        if self.list_inner_type is not None:
            return self._check_if_value_matches_list_type(value)
        if self.dict_types is not None:
            return self._check_if_value_matches_dict_type(value)
        return True

    def _check_if_value_matches_tuple_type(self, value: Any) -> bool:
        """Helper method to check tuple types."""
        if not isinstance(value, tuple) and not isinstance(value, list):
            return False
        assert self.tuple_types is not None
        if len(value) != len(self.tuple_types):
            return False
        return all(_permissive_is_instance(v, t) for v, t in zip(value, self.tuple_types))

    def _check_if_value_matches_list_type(self, value: Any) -> bool:
        """Helper method to check list types."""
        if not isinstance(value, tuple) and not isinstance(value, list):
            return False
        assert self.list_inner_type is not None
        return all(_permissive_is_instance(v, self.list_inner_type) for v in value)

    def _check_if_value_matches_dict_type(self, value: Any) -> bool:
        """Helper method to check dict types."""
        if not isinstance(value, dict):
            return False
        assert self.dict_types is not None
        key_type, value_type = self.dict_types
        return all(
            _permissive_is_instance(k, key_type) and _permissive_is_instance(v, value_type) for k, v in value.items()
        )

    def type_str(self) -> str:
        """Returns a string representation of the type."""
        if self.tuple_types is not None:
            tuple_types_str = ", ".join(t.__name__ for t in self.tuple_types)
            r = "tuple[" + tuple_types_str + "]"
            return r
        if self.list_inner_type is not None:
            r = f"list[{self.list_inner_type.__name__}]"
            return r
        return self.type_.__name__

    def __str__(self) -> str:
        return self.type_str()


class DetailedVar(Generic[DataType]):
    """DetailedVar: A variable with a name, detailed type, and additional explanation."""

    name: str
    type_: DetailedType[DataType]
    explanation: str
    default_value: DataType | Unspecified = UnspecifiedValue
    data_validation_function: Optional[DataValidationFunction[DataType]]

    def __init__(
        self,
        name: str,
        type_: type[DataType],
        explanation: str,
        default_value: DataType | Unspecified,
        *,
        tuple_types: Optional[tuple[type, ...]] = None,
        list_inner_type: Optional[type] = None,
        dict_types: Optional[tuple[type, type]] = None,
        data_validation_function: Optional[DataValidationFunction[DataType]] = None,
    ) -> None:
        self.name = name
        self.explanation = explanation
        self.default_value = default_value
        self.type_ = DetailedType(
            type_, tuple_types=tuple_types, list_inner_type=list_inner_type, dict_types=dict_types
        )
        self.data_validation_function = data_validation_function

    def documentation(self, width_name_and_type: int) -> str:
        """Generates documentation for the variable."""
        name_and_type = f"{self.name} ({self.type_.type_str()})"
        name_and_type_padded = name_and_type.ljust(width_name_and_type)
        return f"{name_and_type_padded}: {self.explanation} (default: {self.default_value})"

    @staticmethod
    def documentation_header() -> list[str]:
        """Generates the header for the documentation."""
        return ["Name", "Type", "Default", "Explanation"]

    def documentation_cells(self) -> list[str]:
        """Generates documentation for the variable, as a list of cells."""
        from textwrap import wrap

        def with_max_width(txt: str, width: int) -> str:
            lines = wrap(txt, width=width)
            return "\n".join(lines)

        return [
            with_max_width(self.name, width=32),
            with_max_width(self.type_.type_str(), width=22),
            with_max_width(str(self.default_value), width=20),
            with_max_width(self.explanation, width=46),
        ]

    def is_value_ok(self, value: Any) -> bool:
        """Checks if the given value is valid."""
        if not self.type_.is_value_type_ok(value):
            return False
        if self.data_validation_function is not None:
            is_valid = True
            try:
                self.data_validation_function(value)
            except ValueError:
                is_valid = False
            return is_valid
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
