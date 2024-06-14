from imgui_bundle import imgui
import fiatlight as fl
from typing import NewType


def usability_single_incompatible_param() -> None:
    """In this example the prompt should not be editable in the node, but it should be editable in the pop-up."""

    def f(prompt: str) -> str:
        return prompt

    def my_str_edit(prompt: str) -> tuple[bool, str]:
        changed, new_prompt = imgui.input_text_multiline("Prompt", prompt)
        return changed, new_prompt

    f_gui = fl.FunctionWithGui(f)

    param_gui = f_gui.param_gui("prompt")

    param_gui.callbacks.edit = my_str_edit
    param_gui.callbacks.edit_node_compatible = False
    param_gui.callbacks.edit_collapsible = True

    fl.run(f_gui, app_name="usability_single_incompatible_param")


StrMultiline = NewType("StrMultiline", str)


class StrMultilineWithGui(fl.AnyDataWithGui[StrMultiline]):
    def __init__(self) -> None:
        super().__init__(StrMultiline)
        self.callbacks.edit = self.edit

        self.callbacks.default_value_provider = lambda: StrMultiline("")

        self.callbacks.present = self.present
        self.callbacks.present_str = self.present_str
        self.callbacks.present_collapsible = True
        self.callbacks.present_node_compatible = False

        self.callbacks.edit = self.edit
        self.callbacks.edit_collapsible = True
        self.callbacks.edit_node_compatible = False

    @staticmethod
    def edit(value: StrMultiline) -> tuple[bool, StrMultiline]:
        changed, new_value = imgui.input_text_multiline("Value", value)
        return changed, StrMultiline(new_value)

    @staticmethod
    def present(value: StrMultiline) -> None:
        imgui.input_text_multiline("Value", value)

    @staticmethod
    def present_str(value: StrMultiline) -> str:
        return f"StrMultiline({value})"


fl.register_type(StrMultiline, StrMultilineWithGui)


def usability_incompatible_registered() -> None:
    """In this example the prompt should not be editable in the node, but it should be editable in the pop-up."""

    def f(prompt: StrMultiline) -> StrMultiline:
        return prompt

    fl.run(f, app_name="usability_incompatible_registered")


def usability_incompatible_param_in_dataclass() -> None:
    """In this example MyData should not be editable in the node, but it should be editable in the pop-up.
    (It should inherit the fact that it cannot be edited in a node from its members)
    """
    from pydantic import BaseModel

    @fl.base_model_with_gui_registration(value__range=(50, 75))
    class MyData(BaseModel):
        prompt1: StrMultiline
        prompt2: StrMultiline
        value: int

    def f(data: MyData) -> MyData:
        return data

    fl.run(f, app_name="usability_incompatible_param_in_dataclass")


def usability_compatible_param_in_dataclass() -> None:
    """In this example MyData should be editable in the node, and it should be editable in the pop-up."""
    from pydantic import BaseModel

    @fl.base_model_with_gui_registration(value__range=(50, 75))
    class MyData(BaseModel):
        value: int
        name: str
        firstname: str

    def f(data: MyData) -> MyData:
        return data

    fl.run(f, app_name="usability_compatible_param_in_dataclass")


if __name__ == "__main__":
    """Choose which example you want to run. When making modifications, all should behave correctly."""
    # usability_single_incompatible_param()
    # usability_incompatible_registered()
    usability_incompatible_param_in_dataclass()
    # usability_compatible_param_in_dataclass()
