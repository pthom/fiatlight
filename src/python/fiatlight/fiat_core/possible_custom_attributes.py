from dataclasses import dataclass
from typing import Any, Optional
from .detailed_type import DetailedVar
from .togui_exception import FiatToGuiException
from fiatlight.fiat_types.base_types import DataType
from fiatlight.fiat_types.function_types import DataValidationFunction, DataValidationResult
from fiatlight.fiat_types.error_types import Unspecified


@dataclass
class _ExplainedSection:
    explanation: str


class PossibleCustomAttributes:
    """PossibleCustomAttributes: a collection of possible custom attributes for a AnyDataWithGui descendant type"""

    parent_name: str  # name of the AnyDataWithGui descendant type
    _explained_attributes_or_section: list[DetailedVar[Any] | _ExplainedSection]

    def __init__(self, parent_name: str) -> None:
        self._explained_attributes_or_section = []
        self.parent_name = parent_name

    def _explained_attributes(self) -> list[DetailedVar[Any]]:
        return [attr for attr in self._explained_attributes_or_section if isinstance(attr, DetailedVar)]

    def add_explained_section(self, explanation: str) -> None:
        self._explained_attributes_or_section.append(_ExplainedSection(explanation))

    def add_explained_attribute(
        self,
        name: str,
        type_: type,
        explanation: str,
        default_value: DataType | Unspecified,
        *,
        tuple_types: Optional[tuple[type, ...]] = None,
        list_inner_type: Optional[type] = None,
        data_validation_function: Optional[DataValidationFunction[DataType]] = None,
    ) -> None:
        self._explained_attributes_or_section.append(
            DetailedVar(
                name,
                type_,
                explanation=explanation,
                default_value=default_value,
                tuple_types=tuple_types,
                list_inner_type=list_inner_type,
                data_validation_function=data_validation_function,
            )
        )

    def _get_explained_attribute(self, name: str) -> DetailedVar[Any] | None:
        for attr in self._explained_attributes():
            if attr.name == name:
                return attr
        return None

    def validate_custom_attrs(self, custom_attrs: dict[str, Any]) -> DataValidationResult:
        unwanted_keys = []
        attributes_with_wrong_type_msgs = []
        attributes_with_failed_validation: dict[str, str] = {}

        for attr_name, value in custom_attrs.items():
            explained_attr = self._get_explained_attribute(attr_name)
            if explained_attr is None:
                unwanted_keys.append(attr_name)
            elif not explained_attr.type_.is_value_type_ok(value):
                msg = f"Attribute {attr_name} should be of type {explained_attr.type_.type_str()}, but it is {type(value)}"
                attributes_with_wrong_type_msgs.append(msg)
            elif explained_attr.data_validation_function is not None:
                data_validation = explained_attr.data_validation_function(value)
                if not data_validation.is_valid:
                    attributes_with_failed_validation[attr_name] = data_validation.error_message

        if (
            len(unwanted_keys) > 0
            or len(attributes_with_wrong_type_msgs) > 0
            or len(attributes_with_failed_validation) > 0
        ):
            msg = ""
            if len(unwanted_keys) > 0:
                unwanted_keys_str = ", ".join(unwanted_keys)
                msg += f"The following custom attributes are not allowed: {unwanted_keys_str}\n\n"
            if len(attributes_with_wrong_type_msgs) > 0:
                msg += "The following custom attributes have wrong types:\n    "
                msg += "\n    ".join(attributes_with_wrong_type_msgs) + "\n\n"
            if len(attributes_with_failed_validation) > 0:
                msg += "The following custom attributes failed validation:\n"
                for attr_name, error_msg in attributes_with_failed_validation.items():
                    msg += f"    {attr_name}: {error_msg}\n"

            return DataValidationResult.error(msg)

        return DataValidationResult.ok()

    def raise_exception_if_bad_custom_attrs(self, custom_attrs: dict[str, Any]) -> None:
        validation_result = self.validate_custom_attrs(custom_attrs)

        if not validation_result.is_valid:
            msg = f"Encountered incorrect attributes for {self.parent_name} !\n"
            msg += "-" * 80 + "\n"
            msg += validation_result.error_message + "\n"
            msg += "-" * 80 + "\n"
            msg_documentation = self.documentation()

            all_msg = [msg]
            all_msg.append(msg_documentation)
            msg = "\n".join(all_msg)
            raise FiatToGuiException(msg)

    def documentation(self) -> str:
        width = 80
        width_name_and_type = 35

        lines = []  # noqa
        lines.append(f"Available custom attributes for {self.parent_name}:")
        lines.append("-" * width)
        for attr in self._explained_attributes_or_section:
            if isinstance(attr, _ExplainedSection):
                lines.append("")
                lines.append(attr.explanation)
                lines.append("-" * width)
            else:
                lines.append(attr.documentation(width_name_and_type))
        return "\n".join(lines)

    def example_usage(self) -> str:
        lines = []  # noqa
        lines.append("(")
        for attr in self._explained_attributes_or_section:
            if isinstance(attr, _ExplainedSection):
                lines.append(f"    #  {attr.explanation}")
            else:
                code = f"    {attr.name} = {attr.default_value},"
                lines.append(code)
        lines.append(")")
        r = "\n".join(lines)
        return r
