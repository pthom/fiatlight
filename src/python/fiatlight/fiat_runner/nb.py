"""Notebook-specific async runner for fiatlight.

This module provides `start()`, `stop()`, and `is_running()` functions for running
fiatlight applications in Jupyter notebooks without blocking the notebook execution.

Usage:
    import fiatlight

    def my_function(x: int) -> int:
        return x * 2

    # Start the GUI (non-blocking)
    fiatlight.nb.start(my_function, app_name="my_app")

    # Check if running
    if fiatlight.nb.is_running():
        print("GUI is running")

    # Stop the GUI
    fiatlight.nb.stop()
"""

import asyncio
from typing import List
from imgui_bundle import hello_imgui

from fiatlight.fiat_core import FunctionsGraph, FunctionWithGui
from fiatlight.fiat_types.function_types import Function
from fiatlight.fiat_runner.fiat_gui import FiatRunParams, run_async

# Global state for tracking the running task
_running_task: asyncio.Task | None = None


def start(
    fn: Function | FunctionWithGui | List[Function | FunctionWithGui] | FunctionsGraph,
    params: FiatRunParams | None = None,
    app_name: str | None = None,
) -> None:
    """Start a fiatlight application asynchronously in a notebook.

    This function returns immediately and runs the GUI in the background.
    Use `stop()` to close the GUI, and `is_running()` to check its status.

    Args:
        fn: A function, FunctionWithGui, list of functions (composition), or FunctionsGraph to run.
        params: Optional FiatRunParams to configure the runner.
        app_name: The application name (required for notebooks to save settings).
                  Will be displayed in the window title.

    Raises:
        RuntimeError: If a fiatlight application is already running.
        ValueError: If app_name is not specified (required in notebooks).
    """
    global _running_task

    if _running_task is not None and not _running_task.done():
        raise RuntimeError("A fiatlight application is already running. Call fiatlight.nb.stop() first.")

    if app_name is None:
        raise ValueError("app_name must be specified when running in a notebook, so that the settings can be saved.")

    if params is None:
        params = FiatRunParams()
    params.app_name = app_name

    # Apply light theme by default for notebooks (better visibility)
    if params.theme is None:
        params.theme = hello_imgui.ImGuiTheme_.white_is_white

    async def _run_wrapper() -> None:
        await run_async(fn, params=params)

    # Get the current event loop or create one
    try:
        loop = asyncio.get_running_loop()
        _running_task = loop.create_task(_run_wrapper())
    except RuntimeError:
        # No running loop, create one (shouldn't happen in Jupyter, but handle gracefully)
        _running_task = asyncio.ensure_future(_run_wrapper())


def stop() -> None:
    """Stop the currently running fiatlight application.

    This requests the application to close gracefully.
    """
    global _running_task

    if _running_task is None or _running_task.done():
        return

    # Request the app to exit
    try:
        hello_imgui.get_runner_params().app_shall_exit = True
    except Exception:
        # Runner might not be initialized yet or already stopped
        pass


def is_running() -> bool:
    """Check if a fiatlight application is currently running.

    Returns:
        True if an application is running, False otherwise.
    """
    global _running_task
    return _running_task is not None and not _running_task.done()


__all__ = [
    "start",
    "stop",
    "is_running",
]
