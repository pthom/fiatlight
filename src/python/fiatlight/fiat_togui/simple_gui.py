"""Helpers to declare a typed pin without subclassing AnyDataWithGui.

`make_simple_gui` and `register_callbacks` accept the fields of
`AnyDataGuiCallbacks` as explicit keyword-only parameters and produce a
factory / a registered type. Explicit kwargs (no `**kwargs: Any`) so
typos are caught by mypy + IDE autocomplete, not at runtime.

See `_plans/anydatawithgui_ergonomics__spec.md` for the design rationale.
"""

from typing import Any, Callable, cast

from fiatlight.fiat_core.any_data_with_gui import AnyDataWithGui
from fiatlight.fiat_core.any_data_gui_callbacks import AnyDataGuiCallbacks
from fiatlight.fiat_types.base_types import FiatAttributes, JsonDict
from fiatlight.fiat_types.function_types import BoolFunction, VoidFunction
from fiatlight.fiat_types.typename_utils import TypeLike

from .gui_registry import GuiFactory, register_type


# Mirror of AnyDataGuiCallbacks's attribute names. A unit test asserts
# this stays in sync with the dataclass and with the explicit signatures
# below.
_CALLBACK_FIELDS: frozenset[str] = frozenset(
    {
        "present_str",
        "present",
        "present_collapsible",
        "present_detachable",
        "edit",
        "edit_collapsible",
        "edit_detachable",
        "default_value_provider",
        "on_change",
        "validators",
        "on_exit",
        "on_heartbeat",
        "on_fiat_attributes_changed",
        "save_gui_options_to_json",
        "load_gui_options_from_json",
        "save_to_dict",
        "load_from_dict",
        "clipboard_copy_str",
        "clipboard_copy_possible",
    }
)


def make_simple_gui(
    type_: TypeLike,
    *,
    # ---- Presentation
    present_str: Callable[[Any], str] | None = None,
    present: Callable[[Any], None] | None = None,
    present_collapsible: bool | None = None,
    present_detachable: bool | None = None,
    # ---- Edition
    edit: Callable[[Any], tuple[bool, Any]] | None = None,
    edit_collapsible: bool | None = None,
    edit_detachable: bool | None = None,
    # ---- Default value
    default: Callable[[], Any] | None = None,
    default_value_provider: Callable[[], Any] | None = None,
    # ---- Events
    on_change: Callable[[Any], None] | None = None,
    validators: list[Callable[[Any], Any]] | None = None,
    on_exit: VoidFunction | None = None,
    on_heartbeat: BoolFunction | None = None,
    on_fiat_attributes_changed: Callable[[FiatAttributes], None] | None = None,
    # ---- Serialization
    save_gui_options_to_json: Callable[[], JsonDict] | None = None,
    load_gui_options_from_json: Callable[[JsonDict], None] | None = None,
    save_to_dict: Callable[[Any], JsonDict] | None = None,
    load_from_dict: Callable[[JsonDict], Any] | None = None,
    # ---- Clipboard
    clipboard_copy_str: Callable[[Any], str] | None = None,
    clipboard_copy_possible: bool | None = None,
    # ---- Escape hatch
    callbacks: AnyDataGuiCallbacks[Any] | None = None,
) -> GuiFactory[Any]:
    """Build a GUI factory for `type_` from explicit per-callback kwargs.

    `default` is an alias for `default_value_provider`; pass at most one.
    `callbacks=AnyDataGuiCallbacks(...)` is an escape hatch — pass *either*
    that *or* per-field kwargs, not both.

    Returns a `GuiFactory` (a no-arg callable producing fresh
    `AnyDataWithGui` instances) ready to pass to `register_type`.
    """
    per_field: dict[str, Any] = {
        "present_str": present_str,
        "present": present,
        "present_collapsible": present_collapsible,
        "present_detachable": present_detachable,
        "edit": edit,
        "edit_collapsible": edit_collapsible,
        "edit_detachable": edit_detachable,
        "default_value_provider": default_value_provider,
        "on_change": on_change,
        "validators": validators,
        "on_exit": on_exit,
        "on_heartbeat": on_heartbeat,
        "on_fiat_attributes_changed": on_fiat_attributes_changed,
        "save_gui_options_to_json": save_gui_options_to_json,
        "load_gui_options_from_json": load_gui_options_from_json,
        "save_to_dict": save_to_dict,
        "load_from_dict": load_from_dict,
        "clipboard_copy_str": clipboard_copy_str,
        "clipboard_copy_possible": clipboard_copy_possible,
    }

    if callbacks is not None:
        any_per_field = any(v is not None for v in per_field.values()) or default is not None
        if any_per_field:
            raise TypeError("make_simple_gui: pass either `callbacks=` OR per-field kwargs, not both.")
        applied: dict[str, Any] = {
            name: getattr(callbacks, name) for name in _CALLBACK_FIELDS if name in callbacks.__dict__
        }
    else:
        if default is not None and default_value_provider is not None:
            raise TypeError(
                "make_simple_gui: 'default' and 'default_value_provider' both target the same field; pass only one."
            )
        applied = {name: value for name, value in per_field.items() if value is not None}
        if default is not None:
            applied["default_value_provider"] = default

    # Helper-specific default overrides: simple pins are small text reads,
    # collapsing them adds visual noise. Authors can override explicitly.
    applied.setdefault("present_collapsible", False)
    applied.setdefault("edit_collapsible", False)

    def factory() -> AnyDataWithGui[Any]:
        gui = AnyDataWithGui[Any](cast(type, type_))
        for name, value in applied.items():
            setattr(gui.callbacks, name, value)
        return gui

    return factory


def register_callbacks(
    type_: TypeLike,
    *,
    # ---- Presentation
    present_str: Callable[[Any], str] | None = None,
    present: Callable[[Any], None] | None = None,
    present_collapsible: bool | None = None,
    present_detachable: bool | None = None,
    # ---- Edition
    edit: Callable[[Any], tuple[bool, Any]] | None = None,
    edit_collapsible: bool | None = None,
    edit_detachable: bool | None = None,
    # ---- Default value
    default: Callable[[], Any] | None = None,
    default_value_provider: Callable[[], Any] | None = None,
    # ---- Events
    on_change: Callable[[Any], None] | None = None,
    validators: list[Callable[[Any], Any]] | None = None,
    on_exit: VoidFunction | None = None,
    on_heartbeat: BoolFunction | None = None,
    on_fiat_attributes_changed: Callable[[FiatAttributes], None] | None = None,
    # ---- Serialization
    save_gui_options_to_json: Callable[[], JsonDict] | None = None,
    load_gui_options_from_json: Callable[[JsonDict], None] | None = None,
    save_to_dict: Callable[[Any], JsonDict] | None = None,
    load_from_dict: Callable[[JsonDict], Any] | None = None,
    # ---- Clipboard
    clipboard_copy_str: Callable[[Any], str] | None = None,
    clipboard_copy_possible: bool | None = None,
    # ---- Escape hatch
    callbacks: AnyDataGuiCallbacks[Any] | None = None,
) -> None:
    """Build a simple GUI for `type_` and register it in one shot.

    Same kwargs as `make_simple_gui`. NewType inputs auto-dispatch via
    `register_type` to the docstring-checking path.
    """
    factory = make_simple_gui(
        type_,
        present_str=present_str,
        present=present,
        present_collapsible=present_collapsible,
        present_detachable=present_detachable,
        edit=edit,
        edit_collapsible=edit_collapsible,
        edit_detachable=edit_detachable,
        default=default,
        default_value_provider=default_value_provider,
        on_change=on_change,
        validators=validators,
        on_exit=on_exit,
        on_heartbeat=on_heartbeat,
        on_fiat_attributes_changed=on_fiat_attributes_changed,
        save_gui_options_to_json=save_gui_options_to_json,
        load_gui_options_from_json=load_gui_options_from_json,
        save_to_dict=save_to_dict,
        load_from_dict=load_from_dict,
        clipboard_copy_str=clipboard_copy_str,
        clipboard_copy_possible=clipboard_copy_possible,
        callbacks=callbacks,
    )
    register_type(cast(type, type_), factory)


__all__ = [
    "make_simple_gui",
    "register_callbacks",
]
