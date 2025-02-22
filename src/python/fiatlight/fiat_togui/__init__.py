from .gui_registry import (
    # ==================
    # Types registration
    # ==================
    register_type,
    # For dataclasses
    register_dataclass,
    dataclass_with_gui_registration,  # (decorator)
    # For pydantic models
    register_base_model,
    base_model_with_gui_registration,  # (decorator)
)
from .to_gui import (
    # ===============================
    # Convert a type or data to a GUI
    # ===============================
    to_data_with_gui,
    any_type_to_gui,
    _to_data_with_gui_impl,
    _any_type_to_gui_impl,
    # ==============================================
    # Factory used when dealing with editable graphs
    # ==============================================
)
from .explained_value_gui import edit_explained_value, make_explained_value_edit_callback
from .file_types_gui import text_from_file, TextToFileGui
from .file_types_gui import _register_file_paths_types
from .immediate_edit import immediate_edit, immedit
from . import dataclass_examples  # noqa (this will register an example dataclass and BaseModel)

_register_file_paths_types()


__all__ = [
    # from to_gui
    "register_type",
    "register_dataclass",
    "dataclass_with_gui_registration",
    "register_base_model",
    "base_model_with_gui_registration",
    "any_type_to_gui",
    "to_data_with_gui",
    "_to_data_with_gui_impl",
    "_any_type_to_gui_impl",
    # from explained_value_gui
    "edit_explained_value",
    "make_explained_value_edit_callback",
    # from file_types_gui
    "text_from_file",
    "TextToFileGui",
    # from immediate_edit
    "immediate_edit",
    "immedit",
]
