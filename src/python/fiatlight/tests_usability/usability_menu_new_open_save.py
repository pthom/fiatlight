"""Hand-run smoke test for File > New / Open / Save / Save As.

Launched with `run_graph_composer`, so the graph starts empty and all
four menu entries are visible. Suggested checks:

1. Drag a couple of nodes from the palette, wire them up.
2. File > Save As… → pick `~/foo.fiat_workspace.json`. A single file is
   written; focused-mode visibility rides along inside the workspace.
3. Quit. Relaunch the script: the workspace is restored from
   `~/foo.fiat_workspace.json` (the cursor was persisted via
   hello_imgui's user-pref storage, inside the per-app .ini).
4. File > New Workspace → canvas clears, and the cursor resets to the
   default per-app autosave path. Quit + relaunch resumes empty.
5. File > Open Workspace… → pick `foo.fiat_workspace.json` again.
   Positions, labels, and focused-mode flags round-trip.

In programmatic mode (a script that calls `fl.run(graph, ...)` with a
pre-built graph), the File menu hides New (the topology comes from
code) but keeps Open / Save / Save As. Open then overlays parameter
values and GUI options from the picked file onto the code-defined
graph; the topology is not replaced.
"""

import math

import fiatlight as fl


@fl.with_fiat_attributes(fiat_tags=["math"])
def cos(x: float) -> float:
    return math.cos(math.radians(x))


@fl.with_fiat_attributes(fiat_tags=["math"])
def sin(x: float) -> float:
    return math.sin(math.radians(x))


@fl.with_fiat_attributes(fiat_tags=["source"])
def float_source(x: float) -> float:
    return x


if __name__ == "__main__":
    fl.run_graph_composer(
        functions=[float_source, cos, sin],
        app_name="usability_menu_new_open_save",
    )
