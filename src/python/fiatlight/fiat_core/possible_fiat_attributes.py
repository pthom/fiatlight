from dataclasses import dataclass
from typing import Any, Optional
from .detailed_type import DetailedVar
from .togui_exception import FiatToGuiException
from fiatlight.fiat_types.base_types import DataType
from fiatlight.fiat_types.function_types import DataValidationFunction
from fiatlight.fiat_types.error_types import Unspecified


@dataclass
class _ExplainedSection:
    explanation: str


class PossibleFiatAttributes:
    """PossibleFiatAttributes: a collection of possible custom attributes for a AnyDataWithGui descendant type"""

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
        dict_types: Optional[tuple[type, type]] = None,
        data_validation_function: Optional[DataValidationFunction[DataType]] = None,
    ) -> None:
        self._explained_attributes_or_section.append(
            DetailedVar(
                name,
                type_,  # noqa
                explanation=explanation,
                default_value=default_value,
                tuple_types=tuple_types,
                list_inner_type=list_inner_type,
                dict_types=dict_types,
                data_validation_function=data_validation_function,
            )
        )

    def _get_explained_attribute(self, name: str) -> DetailedVar[Any] | None:
        for attr in self._explained_attributes():
            if attr.name == name:
                return attr
        return None

    def merge_attributes(self, other: "PossibleFiatAttributes") -> None:
        self._explained_attributes_or_section += other._explained_attributes_or_section

    def validate_fiat_attrs(self, fiat_attrs: dict[str, Any]) -> None:
        unwanted_keys = []
        attributes_with_wrong_type_msgs = []
        attributes_with_failed_validation: dict[str, str] = {}

        for attr_name, value in fiat_attrs.items():
            explained_attr = self._get_explained_attribute(attr_name)
            if explained_attr is None:
                unwanted_keys.append(attr_name)
            elif not explained_attr.type_.is_value_type_ok(value):
                msg = f"Attribute {attr_name} should be of type {explained_attr.type_.type_str()}, but it is {type(value)}"  # noqa
                attributes_with_wrong_type_msgs.append(msg)
            elif explained_attr.data_validation_function is not None:
                try:
                    explained_attr.data_validation_function(value)
                except ValueError as e:
                    attributes_with_failed_validation[attr_name] = str(e)

        accept_wrong_keys = True  # This check is too complex
        if (
            (len(unwanted_keys) > 0 and not accept_wrong_keys)
            or len(attributes_with_wrong_type_msgs) > 0
            or len(attributes_with_failed_validation) > 0
        ):
            msg = ""
            # if len(unwanted_keys) > 0:
            #     unwanted_keys_str = ", ".join(unwanted_keys)
            #     msg += f"The following fiat attributes are not allowed: {unwanted_keys_str}\n\n"
            if len(attributes_with_wrong_type_msgs) > 0:
                msg += "The following fiat attributes have wrong types:\n    "
                msg += "\n    ".join(attributes_with_wrong_type_msgs) + "\n\n"
            if len(attributes_with_failed_validation) > 0:
                msg += "The following fiat attributes failed validation:\n"
                for attr_name, error_msg in attributes_with_failed_validation.items():
                    msg += f"    {attr_name}: {error_msg}\n"

            raise ValueError(msg)

    def raise_exception_if_bad_fiat_attrs(self, fiat_attrs: dict[str, Any]) -> None:
        is_valid = True
        error_message = ""
        try:
            self.validate_fiat_attrs(fiat_attrs)
        except ValueError as e:
            is_valid = False
            error_message = str(e)

        if not is_valid:
            msg = f"Encountered incorrect attributes for {self.parent_name} !\n"
            msg += "-" * 80 + "\n"
            msg += error_message + "\n"
            msg += "-" * 80 + "\n"
            msg_documentation = self.documentation()

            all_msg = [msg]  # noqa
            all_msg.append(msg_documentation)
            msg = "\n".join(all_msg)
            raise FiatToGuiException(msg)

    def documentation(self) -> str:
        width = 80

        intro = f"Available fiat attributes for {self.parent_name}:"
        intro += "\n" + "-" * width

        # Nice table with tabulate
        from tabulate import tabulate, SEPARATING_LINE  # noqa
        from textwrap import wrap  # noqa

        tabulate_cells: list[list[str]] = []
        for attr in self._explained_attributes_or_section:
            row_cells: list[str] = []
            if isinstance(attr, _ExplainedSection):

                def with_max_width(txt: str, width: int) -> str:
                    lines = wrap(txt, width=width)
                    return "\n".join(lines)

                row_cells = ["", "", "", with_max_width(f"**{attr.explanation}**", 46)]
            else:
                row_cells = attr.documentation_cells()
            tabulate_cells.append(row_cells)

        table = tabulate(tabulate_cells, headers=DetailedVar.documentation_header(), tablefmt="grid")
        r = intro + "\n" + table
        return r

    def example_usage(self, param_name: str) -> str:
        lines = []  # noqa
        for i, attr in enumerate(self._explained_attributes_or_section):
            if isinstance(attr, _ExplainedSection):
                lines.append(f"    #  {attr.explanation}")
            else:
                attr_default_value = str(attr.default_value)
                if isinstance(attr.default_value, str):
                    attr_default_value = f'"{attr_default_value}"'
                code = f"    {param_name}__{attr.name} = {attr_default_value}"
                if i < len(self._explained_attributes_or_section) - 1:
                    code += ","
                lines.append(code)
        r = "\n".join(lines)
        return r


_EMPTY_FIAT_ATTRS = PossibleFiatAttributes("")


def empty_fiat_attrs() -> PossibleFiatAttributes:
    return _EMPTY_FIAT_ATTRS
