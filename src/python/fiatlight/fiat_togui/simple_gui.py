"""Helpers to declare a typed pin without subclassing AnyDataWithGui.

`make_simple_gui` and `register_callbacks` accept callback fields as
kwargs (mirror of `AnyDataGuiCallbacks`) and produce a factory / a
registered type. See `_plans/anydatawithgui_ergonomics__spec.md` for the
design rationale.
"""

from typing import Any, NewType, cast

from fiatlight.fiat_core.any_data_with_gui import AnyDataWithGui
from fiatlight.fiat_core.any_data_gui_callbacks import AnyDataGuiCallbacks
from fiatlight.fiat_types.typename_utils import TypeLike

from .gui_registry import GuiFactory, register_type, register_typing_new_type


# Mirror of AnyDataGuiCallbacks's attribute names. A unit test asserts
# this stays in sync with the dataclass.
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

# Convenience aliases accepted at the kwargs surface but mapped to a
# real callback field before being applied.
_KWARG_ALIASES: dict[str, str] = {
    "default": "default_value_provider",
}


def _resolve_kwargs(kwargs: dict[str, Any]) -> dict[str, Any]:
    """Apply aliases, reject unknowns, reject duplicate-via-alias."""
    resolved: dict[str, Any] = {}
    for name, value in kwargs.items():
        target = _KWARG_ALIASES.get(name, name)
        if target not in _CALLBACK_FIELDS:
            raise TypeError(
                f"make_simple_gui: unknown callback {name!r}. "
                f"Accepted: {sorted(_CALLBACK_FIELDS | _KWARG_ALIASES.keys())}"
            )
        if target in resolved:
            other = next(k for k in kwargs if _KWARG_ALIASES.get(k, k) == target and k != name)
            raise TypeError(f"make_simple_gui: {name!r} and {other!r} both target " f"{target!r}; pass only one.")
        resolved[target] = value
    return resolved


def make_simple_gui(type_: TypeLike, **kwargs: Any) -> GuiFactory[Any]:
    """Build a GUI factory for `type_` from a declarative bag of callbacks.

    Accepts any subset of `AnyDataGuiCallbacks` fields as keyword arguments,
    plus `default` as an alias for `default_value_provider`. An optional
    `callbacks=AnyDataGuiCallbacks(...)` may be passed instead of per-field
    kwargs (mutually exclusive).

    Returns a `GuiFactory` (a no-arg callable producing fresh
    `AnyDataWithGui` instances) that can be passed to `register_type`.
    """
    callbacks_obj: AnyDataGuiCallbacks[Any] | None = kwargs.pop("callbacks", None)
    if callbacks_obj is not None and kwargs:
        raise TypeError("make_simple_gui: pass either `callbacks=` OR per-field kwargs, " "not both.")

    if callbacks_obj is not None:
        applied = {
            name: getattr(callbacks_obj, name)
            for name in _CALLBACK_FIELDS
            # Only apply fields that were set (i.e. instance dict, not class default).
            if name in callbacks_obj.__dict__
        }
    else:
        applied = _resolve_kwargs(kwargs)

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


def register_callbacks(type_: TypeLike, **kwargs: Any) -> None:
    """Build a simple GUI for `type_` and register it in one shot.

    Equivalent to `register_type(type_, make_simple_gui(type_, **kwargs))`,
    except that NewType inputs go through the docstring-checking path so
    the registry can still complain if the NewType is undocumented.
    """
    factory = make_simple_gui(type_, **kwargs)
    if isinstance(type_, NewType):
        register_typing_new_type(type_, factory)
    else:
        register_type(cast(type, type_), factory)


__all__ = [
    "make_simple_gui",
    "register_callbacks",
]
