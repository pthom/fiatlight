AnyDataGuiCallbacks
===================

Introduction
------------

AnyDataGuiCallbacks provides a set of callbacks that define how a particular data type should be presented, edited, and managed within the Fiatlight GUI framework.

These callbacks are used by [AnyDataWithGui](api_any_data_with_gui).

Source
------

Below, is the class source, which you can also see [online](FL_GH_ROOT/fiat_core/any_data_gui_callbacks.py).

```python
from fiatlight.fiat_notebook import look_at_code
%look_at_python_code fiatlight.fiat_core.AnyDataGuiCallbacks
```

Architecture
------------

Below is a PlantUML diagram showing the architecture of the `fiat_core` module.
See the [architecture page](api_architecture) for the full architecture diagrams.

    ```python
    from fiatlight.fiat_notebook import plantuml_magic
    %plantuml_include class_diagrams/fiat_core.puml
    ```
