from dataclasses import dataclass
from typing import Any


@dataclass
class _ExplainedSection:
    explanation: str


@dataclass
class _ExplainedAttribute:
    name: str
    type_: type
    explanation: str
    type_details: str | None = None

    def is_value_ok(self, value: Any) -> bool:
        # Special case for int that can be converted to float
        if self.type_ == float and isinstance(value, int):
            return True
        if not isinstance(value, self.type_):
            return False
        if self.type_details is None:
            return True

        if self.type_details == "(int, int)":
            if not isinstance(value, tuple) or len(value) != 2:
                return False
            if not all([isinstance(v, int) for v in value]):
                return False
            return True
        elif self.type_details == "(float, float)":
            if not isinstance(value, tuple) or len(value) != 2:
                return False
            if not all([isinstance(v, float) or isinstance(v, int) for v in value]):
                return False
            return True
        else:
            return True

    def type_str(self) -> str:
        if self.type_details is None:
            return self.type_.__name__
        else:
            return self.type_details


class PossibleCustomAttributes:
    """PossibleCustomAttributes: a collection of possible custom attributes for a data type"""

    _explained_attributes_or_section: list[_ExplainedAttribute | _ExplainedSection]
    _widget_description: str

    def __init__(self, widget_description: str) -> None:
        self._explained_attributes_or_section = []
        self._widget_description = widget_description

    def _explained_attributes(self) -> list[_ExplainedAttribute]:
        return [attr for attr in self._explained_attributes_or_section if isinstance(attr, _ExplainedAttribute)]

    def add_explained_section(self, explanation: str) -> None:
        self._explained_attributes_or_section.append(_ExplainedSection(explanation))

    def add_explained_attribute(
        self, name: str, type_: type, explanation: str, type_details: str | None = None
    ) -> None:
        self._explained_attributes_or_section.append(_ExplainedAttribute(name, type_, explanation, type_details))

    def _get_explained_attribute(self, name: str) -> _ExplainedAttribute | None:
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
            elif not explained_attr.is_value_ok(value):
                msg = f"Attribute {attr_name} should be of type {explained_attr.type_str()}, but it is {type(value)}"
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
            raise ValueError(msg)

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
                # pad the name to width_name
                name_and_type = f"{attr.name}"
                if attr.type_details is not None:
                    name_and_type += f" ({attr.type_details})"
                else:
                    name_and_type += f" ({attr.type_.__name__})"
                name_and_type_padded = name_and_type.ljust(width_name_and_type)
                explanation = attr.explanation
                msg = f"{name_and_type_padded}: {explanation}"
                lines.append(msg)
        return "\n".join(lines)
