"""Hand-run smoke test: same function added twice in one graph.

Demonstrates the two ways `add_link` can address such nodes:

1. By string: pass the `label` you gave the node when adding it.
2. By handle: capture the FunctionNode that `add_function` returns and
   pass it directly. Use this when you didn't set a unique label, or
   when you want to be explicit.

Without a unique label *and* without a captured handle, string addressing
is ambiguous and `add_link` raises with a message pointing at this pattern.

Run the file directly to launch the GUI:
    python -m fiatlight.tests_usability.usability_fn_twice
"""

import math

import fiatlight as fl


def float_source(x: float) -> float:
    return x


def cos(x: float) -> float:
    return math.cos(math.radians(x))


graph = fl.FunctionsGraph()

# --- Option 1: address by label ----------------------------------------
# Each cos node gets a unique `label`, which `add_link` happily accepts as
# its string identifier.
# graph.add_function(float_source)
# graph.add_function(cos, label="cos1")
# graph.add_function(cos, label="cos2")
# graph.add_link(float_source, "cos1")
# graph.add_link("cos1", "cos2")

# --- Option 2: address by node handle ------------------
# Same wiring, but using the FunctionNode handles. Equivalent to option 1
# above; uncomment to try it.
#
n_src = graph.add_function(float_source)
n_cos1 = graph.add_function(cos, label="cos1")
n_cos2 = graph.add_function(cos, label="cos2")
graph.add_link(n_src, n_cos1)
graph.add_link(n_cos1, n_cos2)


if __name__ == "__main__":
    fl.run(
        graph,
        app_name="usability_fn_twice",
        params=fl.FiatRunParams(),  # delete_settings=True),
    )
