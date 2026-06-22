"""Screenshot a fiatlight graph for visual self-validation.

`capture_graph` builds a graph in a real (briefly flashing) window, lets it settle
for a few frames, auto-exits, and writes the node-cropped framebuffer to a PNG, so
a node-rendering change can be eyeballed without a manual smoke test.

Reuses what the app already does on exit (`hello_imgui.final_app_window_screenshot`
cropped to the node bounds, stored via `get_last_screenshot`); the only added wiring
is an "exit after N frames" callback injected on top of `FiatGui._setup_runner`.

Caveats: needs a real GL context (not headless without Xvfb); the window flashes for
~150 ms; on retina the PNG is 2× the logical `window_size`. A throwaway settings file
lands under `fiat_settings/` (already git-ignored).
"""
from __future__ import annotations

from typing import Sequence, Union

from imgui_bundle import immapp

from fiatlight.fiat_core import FunctionsGraph, FunctionWithGui
from fiatlight.fiat_types import Function
from fiatlight.fiat_runner.fiat_gui import FiatGui, FiatRunParams, get_last_screenshot

GraphOrFunctions = Union[FunctionsGraph, Sequence[Union[Function, FunctionWithGui]]]


def capture_graph(
    graph_or_functions: GraphOrFunctions,
    output_path: str,
    *,
    frames: int = 25,
    window_size: tuple[int, int] = (1000, 700),
    invoke: bool = True,
) -> str:
    """Run `graph_or_functions` for `frames` frames, then save a node-cropped PNG.

    `graph_or_functions` is either a ready-built `FunctionsGraph` (build whatever
    wiring you want to validate) or a flat list of functions (added unlinked).
    Returns `output_path`. Raises if nothing was captured (e.g. empty graph).
    """
    if isinstance(graph_or_functions, FunctionsGraph):
        graph = graph_or_functions
    else:
        graph = FunctionsGraph.create_empty()
        for f in graph_or_functions:
            graph.add_function(f)

    params = FiatRunParams(app_name="fiat_capture", window_size=window_size)
    fiat_gui = FiatGui(graph, params=params)
    if invoke:
        fiat_gui._functions_graph_gui.invoke_all_functions(also_invoke_manual_function=False)

    runner_params, addons = fiat_gui._setup_runner()
    # Deterministic capture: start from a clean imgui window layout so a leftover
    # debug window / dock state from a previous run can't leak into the shot.
    # (Don't fully `ini_disable` — the app derives its workspace path from the
    # settings location, which that would break.)
    runner_params.ini_clear_previous_settings = True
    prev_after_swap = runner_params.callbacks.after_swap
    counter = {"n": 0}
    # Lay the nodes out a few frames in, once they've been drawn once so their
    # sizes are known (laying out on frame 0 uses stale sizes -> overlaps).
    layout_at = 4

    def after_swap() -> None:
        if prev_after_swap is not None:
            prev_after_swap()
        counter["n"] += 1
        if counter["n"] == layout_at:
            fiat_gui._functions_graph_gui.request_layout_graph()
        if counter["n"] >= frames:
            runner_params.app_shall_exit = True

    runner_params.callbacks.after_swap = after_swap
    immapp.run(runner_params, addons)

    image = get_last_screenshot()
    if image is None:
        raise RuntimeError("capture_graph: no screenshot captured (is the graph empty?)")

    from PIL import Image

    Image.fromarray(image).save(output_path)
    return output_path
