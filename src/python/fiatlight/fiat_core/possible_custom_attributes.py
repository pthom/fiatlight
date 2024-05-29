from dataclasses import dataclass
from typing import Any, Optional
from .detailed_type import DetailedVar
from .togui_exception import FiatToGuiException


@dataclass
class _ExplainedSection:
    explanation: str


class PossibleCustomAttributes:
    """PossibleCustomAttributes: a collection of possible custom attributes for a data type"""

    _explained_attributes_or_section: list[DetailedVar[Any] | _ExplainedSection]
    _widget_description: str

    def __init__(self, widget_description: str) -> None:
        self._explained_attributes_or_section = []
        self._widget_description = widget_description

    def _explained_attributes(self) -> list[DetailedVar[Any]]:
        return [attr for attr in self._explained_attributes_or_section if isinstance(attr, DetailedVar)]

    def add_explained_section(self, explanation: str) -> None:
        self._explained_attributes_or_section.append(_ExplainedSection(explanation))

    def add_explained_attribute(
        self,
        name: str,
        type_: type,
        explanation: str,
        *,
        tuple_types: Optional[tuple[type, ...]] = None,
        list_inner_type: Optional[type] = None,
    ) -> None:
        self._explained_attributes_or_section.append(
            DetailedVar(
                name,
                type_,
                explanation=explanation,
                tuple_types=tuple_types,
                list_inner_type=list_inner_type,
            )
        )

    def _get_explained_attribute(self, name: str) -> DetailedVar[Any] | None:
        for attr in self._explained_attributes():
            if attr.name == name:
                return attr
        return None

    def _get_error_message(self, custom_attrs: dict[str, Any]) -> str | None:
        unwanted_keys = []
        attributes_with_wrong_type_msgs = []

        for attr_name, value in custom_attrs.items():
            explained_attr = self._get_explained_attribute(attr_name)
            if explained_attr is None:
                unwanted_keys.append(attr_name)
            elif not explained_attr.type_.is_value_ok(value):
                msg = f"Attribute {attr_name} should be of type {explained_attr.type_.type_str()}, but it is {type(value)}"
                attributes_with_wrong_type_msgs.append(msg)

        if len(unwanted_keys) > 0 or len(attributes_with_wrong_type_msgs) > 0:
            msg = ""
            if len(unwanted_keys) > 0:
                unwanted_keys_str = ", ".join(unwanted_keys)
                msg += f"The following custom attributes are not allowed: {unwanted_keys_str}\n\n"
            if len(attributes_with_wrong_type_msgs) > 0:
                msg += "The following custom attributes have wrong types:\n    "
                msg += "\n    ".join(attributes_with_wrong_type_msgs)

            return msg

        return None

    def raise_exception_if_bad_custom_attrs(self, custom_attrs: dict[str, Any]) -> None:
        error_message = self._get_error_message(custom_attrs)

        if error_message is not None:
            msg = f"Encountered incorrect attributes for {self._widget_description} !\n"
            msg += "-" * 80 + "\n"
            msg += error_message + "\n"
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
        lines.append(f"Here are the available custom attributes for {self._widget_description}:\n\n")
        lines.append("-" * width)
        for attr in self._explained_attributes_or_section:
            if isinstance(attr, _ExplainedSection):
                lines.append("")
                lines.append(attr.explanation)
                lines.append("-" * width)
            else:
                lines.append(attr.documentation(width_name_and_type))
        return "\n".join(lines)
