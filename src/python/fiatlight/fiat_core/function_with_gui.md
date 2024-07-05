FunctionWithGui
===============

Introduction
------------

`FunctionWithGui` is one of the core classes of FiatLight: it wraps a function with a GUI that presents its inputs and outputs.

* **Manual**: Read the [manual](manual_function) for a detailed guide on how to use it.
* **Source code**: View its full code [online](FL_GH_ROOT/fiat_core/function_with_gui.py).


Signature
---------

Below, you will find the "signature" of the `FunctionWithGui` class,
with its main attributes and methods (but not their bodies)

Its full source code is [available online](FL_GH_ROOT/fiat_core/function_with_gui.py).

```python
from fiatlight.fiat_notebook import look_at_code
%look_at_class_header fiatlight.fiat_core.FunctionWithGui
```

Architecture
------------

Below is a PlantUML diagram showing the architecture of the `fiat_core` module.
See the [architecture page](api_architecture) for the full architecture diagrams.

```python
from fiatlight.fiat_notebook import plantuml_magic
%plantuml_include class_diagrams/fiat_core.puml
```
