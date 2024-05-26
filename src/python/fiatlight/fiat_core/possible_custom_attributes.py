from dataclasses import dataclass
from typing import Any


class PossibleCustomAttributes:
    """PossibleCustomAttributes: a collection of possible custom attributes for a data type"""

    @dataclass
    class ExplainedSection:
        explanation: str

    @dataclass
    class ExplainedAttribute:
        name: str
        type_: type
        explanation: str
        type_details: str | None = None

    _explained_attributes_or_section: list[ExplainedAttribute | ExplainedSection]

    def __init__(self) -> None:
        self._explained_attributes_or_section = []

    def _explained_attributes(self) -> list[ExplainedAttribute]:
        return [attr for attr in self._explained_attributes_or_section if isinstance(attr, self.ExplainedAttribute)]

    def add_explained_section(self, explanation: str) -> None:
        self._explained_attributes_or_section.append(self.ExplainedSection(explanation))

    def add_explained_attribute(
        self, name: str, type_: type, explanation: str, type_details: str | None = None
    ) -> None:
        self._explained_attributes_or_section.append(self.ExplainedAttribute(name, type_, explanation, type_details))

    def _are_custom_attrs_ok(self, custom_attrs: dict[str, Any]) -> bool:
        explained_attributes_names = [attr.name for attr in self._explained_attributes()]
        has_unwanted_key = any([attr not in explained_attributes_names for attr in custom_attrs.keys()])
        if has_unwanted_key > 0:
            return False

        attributes_with_wrong_type = []
        for attr in self._explained_attributes():
            if attr.name in custom_attrs and not isinstance(custom_attrs[attr.name], attr.type_):
                attributes_with_wrong_type.append(attr.name)
        if len(attributes_with_wrong_type) > 0:
            return False

        return True

    def _explain_unwanted_keys(self, custom_attrs: dict[str, Any]) -> str:
        explained_attributes = self._explained_attributes()
        unwanted_keys = set(custom_attrs.keys()) - set([attr.name for attr in explained_attributes])
        unwanted_keys_str = ", ".join(unwanted_keys)
        if len(unwanted_keys) > 0:
            msg = f"The following custom attributes are not allowed: {unwanted_keys_str}\n\n"
            return msg
        else:
            return ""

    def _explain_wrong_types(self, custom_attrs: dict[str, Any]) -> str:
        msgs = []
        for attr in self._explained_attributes():
            if attr.name in custom_attrs and not isinstance(custom_attrs[attr.name], attr.type_):
                msg = f"Attribute {attr.name} should be of type {attr.type_}, but it is {type(custom_attrs[attr.name])}"
                msgs.append(msg)
        if len(msgs) > 0:
            msg = "The following custom attributes have wrong types:\n"
            msg += "\n".join(msgs)
            return msg
        else:
            return ""

    def raise_exception_if_bad_custom_attrs(self, custom_attrs: dict[str, Any], widget_description: str) -> None:
        if not self._are_custom_attrs_ok(custom_attrs):
            msg = f"Encountered incorrect attributes for {widget_description} !\n"
            msg += "-" * len(msg) + "\n"
            msg_key_errors = self._explain_unwanted_keys(custom_attrs)
            msg_type_errors = self._explain_wrong_types(custom_attrs)
            msg_documentation = self.documentation()
            all_msg = [msg]
            if len(msg_key_errors) > 0:
                all_msg.append(msg_key_errors)
            if len(msg_type_errors) > 0:
                all_msg.append(msg_type_errors)
            all_msg.append(msg_documentation)
            msg = "\n".join(all_msg)
            raise ValueError(msg)

    def documentation(self) -> str:
        lines = []
        width = 80
        width_name_and_type = 35
        for attr in self._explained_attributes_or_section:
            if isinstance(attr, self.ExplainedSection):
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
