"""TaskNode: A function node that returns nothing and performs a task when the inputs change
"""
from fiatlight.fiat_core.function_with_gui import FunctionWithGui
from typing import Any, Callable


class TaskNode(FunctionWithGui):
    def __init__(
        self,
        fn: Callable[..., Any],
        label: str | None = None,
    ) -> None:
        self._accept_none_as_output = True
        super().__init__(fn)
        self.function_name = fn.__name__
        self.label = label if label is not None else self.function_name
