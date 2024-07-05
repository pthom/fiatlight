AnyDataWithGui
==============

Introduction
------------

AnyDataWithGui associate a GUI to any type, with associated GUI callbacks, allowing for custom rendering, editing, serialization, and event handling within the Fiatlight framework.

It uses callbacks which are stored inside [AnyDataGuiCallback](api_any_data_gui_callbacks.ipynb).

Signature
---------

Below, we display the class header, i.e., the class without its methods bodies, to give a quick overview of its structure.

You can see its full code at [AnyDataWithGui](FL_GH_ROOT/fiat_core/any_data_with_gui.py).

```python
from fiatlight.fiat_notebook import look_at_code
%look_at_class_header fiatlight.fiat_core.AnyDataWithGui
```

Architecture
------------

Below is a PlantUML diagram showing the architecture of the `fiat_core` module.
See the [architecture page](api_architecture) for the full architecture diagrams.

    ```python
    from fiatlight.fiat_notebook import plantuml_magic
    %plantuml_include class_diagrams/fiat_core.puml
    ```
