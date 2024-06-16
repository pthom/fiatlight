import pydantic
import logging


class _ToGuiContext(pydantic.BaseModel):
    last_typenames_handled: list[str] = pydantic.Field(default_factory=list)
    last_functions_handled: list[str] = pydantic.Field(default_factory=list)
    missing_gui_factories: list[str] = pydantic.Field(default_factory=list)

    def enqueue_typename(self, typename: str) -> None:
        if len(self.last_typenames_handled) > 0 and self.last_typenames_handled[-1] == typename:
            return
        self.last_typenames_handled.append(typename)

    def enqueue_function(self, function_name: str) -> None:
        if len(self.last_functions_handled) > 0 and self.last_functions_handled[-1] == function_name:
            return
        self.last_functions_handled.append(function_name)

    def add_missing_gui_factory(self, typename: str) -> None:
        if typename in self.missing_gui_factories:
            return
        logging.warning(f"Type {typename} not registered in gui_factories()")
        self.missing_gui_factories.append(typename)

    def info(self) -> str:
        # Return the 3 last typenames and functions handled
        from fiatlight.fiat_doc import code_utils

        last_typenames_handled = "\n".join(self.last_typenames_handled[-3:])
        last_typenames_handled = "\n" + code_utils.indent_code(last_typenames_handled, 4)
        last_functions_handled = "\n".join(self.last_functions_handled[-3:])
        last_functions_handled = "\n" + code_utils.indent_code(last_functions_handled, 4)
        all_missing_gui_factories = "\n".join(self.missing_gui_factories)
        all_missing_gui_factories = "\n" + code_utils.indent_code(all_missing_gui_factories, 4)

        intro = (
            "It seems you experience an error during the transformation of a type or function into a GUI. "
            "To help you, here is some context about the GUI creation:\n"
        )
        outro = "(most recent functions and typenames are at the bottom)"

        msg = intro

        if len(self.missing_gui_factories) > 0:
            msg += "Missing GUI factories:" + all_missing_gui_factories + "\n"

        msg += "Last typenames transformed to GUI:" + last_typenames_handled + "\n"
        msg += "Last functions transformed to GUI:" + last_functions_handled + "\n"
        msg += outro

        return msg


TO_GUI_CONTEXT = _ToGuiContext()


def to_gui_context_info() -> str:
    return TO_GUI_CONTEXT.info()
