FunctionsGraph
==============

`FunctionsGraph` is one of the core classes of FiatLight: it represents a graph of functions,
where the output of one function can be linked to the input of another function.

* **Source**: see its full code [online](FL_GH_ROOT/fiat_core/functions_graph.py)
* **Manual**: [FunctionsGraph API](manual_functions_graph)

Signature
---------

Below, you will find the "signature" of the `FunctionsGraph` class,
with its main attributes and methods (but not their bodies)

Its full source code is [available online](../fiat_core/functions_graph.py).

    ```python
    from fiatlight.fiat_notebook import look_at_code
    %look_at_class_header fiatlight.fiat_core.FunctionsGraph
    ```

Architecture
------------

Below is a PlantUML diagram showing the architecture of the `fiat_core` module.
See the [architecture page](api_architecture) for the full architecture diagrams.

    ```python
    from fiatlight.fiat_notebook import plantuml_magic
    %plantuml_include class_diagrams/fiat_core.puml
    ```

