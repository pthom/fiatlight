from enum import Enum
from fiatlight import fiat_utils
from fiatlight.fiat_types.base_types import JsonDict, DataType
from typing import Generic, Dict


class FunctionNodePresentationState(Enum):
    INSIDE_NODE = 0
    FOCUSED = 1

    @staticmethod
    def current_state() -> "FunctionNodePresentationState":
        if fiat_utils.is_rendering_in_node():
            return FunctionNodePresentationState.INSIDE_NODE
        else:
            return FunctionNodePresentationState.FOCUSED


class ValueInNodeVsFocused(Generic[DataType]):
    """A value that can have two different values, depending on the current presentation mode
    (inside node editor, or in a "focused" function,
     i.e. a function that is being displayed in a separate tab).
    """

    value_inside_node: DataType
    value_focused: DataType

    def __init__(self, value_inside_node: DataType, value_focused: DataType) -> None:
        self.value_inside_node = value_inside_node
        self.value_focused = value_focused

    def value(self, state: FunctionNodePresentationState) -> DataType:
        if state == FunctionNodePresentationState.INSIDE_NODE:
            return self.value_inside_node
        elif state == FunctionNodePresentationState.FOCUSED:
            return self.value_focused
        else:
            raise ValueError(f"Unknown state {state}")

    def current_value(self) -> DataType:
        state = FunctionNodePresentationState.current_state()
        return self.value(state)

    def set_current_value(self, value: DataType) -> None:
        state = FunctionNodePresentationState.current_state()
        self._set_value(value, state)

    def _set_value(self, value: DataType, state: FunctionNodePresentationState) -> None:
        if state == FunctionNodePresentationState.INSIDE_NODE:
            self.value_inside_node = value
        elif state == FunctionNodePresentationState.FOCUSED:
            self.value_focused = value
        else:
            raise ValueError(f"Unknown state {state}")


class ExpandedFlagInNodeVsFocused(ValueInNodeVsFocused[bool]):
    """A boolean flag that can be used to control the expanded state of a node in the function graph,
    with different values for when the presentation mode is inside in node vs a "focused" function
    (i.e. a function that is being displayed in a separate tab).
    """

    def __init__(self, expanded_inside_node: bool = False, expanded_focused: bool = True) -> None:
        super().__init__(expanded_inside_node, expanded_focused)

    def save_to_dict(self) -> JsonDict:
        return {
            "inside_node": self.value_inside_node,
            "focused": self.value_focused,
        }

    @staticmethod
    def load_from_dict(d: JsonDict | bool) -> "ExpandedFlagInNodeVsFocused":
        if isinstance(d, bool):
            # This is for backwards compatibility
            return ExpandedFlagInNodeVsFocused(expanded_inside_node=d)
        assert isinstance(d, dict)
        return ExpandedFlagInNodeVsFocused(
            expanded_inside_node=d["inside_node"],
            expanded_focused=d["focused"],
        )


FlagsDict = Dict[str, bool]


class FlagsDictInNodeVsFocused(ValueInNodeVsFocused[FlagsDict | None]):
    def __init__(self, value_inside_node: FlagsDict | None = None, value_focused: FlagsDict | None = None) -> None:
        super().__init__(value_inside_node, value_focused)

    def save_to_dict(self) -> JsonDict:
        return {
            "inside_node": self.value_inside_node,
            "focused": self.value_focused,
        }

    @staticmethod
    def load_from_dict(d: JsonDict | Dict[str, bool] | None) -> "FlagsDictInNodeVsFocused":
        assert isinstance(d, dict)
        value_inside_node = d.get("inside_node", None)
        value_focused = d.get("inside_node", None)
        assert value_inside_node is None or isinstance(value_inside_node, dict)
        assert value_focused is None or isinstance(value_focused, dict)
        return FlagsDictInNodeVsFocused(
            value_inside_node=value_inside_node,
            value_focused=value_focused,
        )
