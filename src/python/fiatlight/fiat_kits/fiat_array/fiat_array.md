fiat_array: widget for 1D and 2D numpy arrays
=============================================

Fiatlight provides `SimplePlotGui`, a viewer for numpy arrays that allows to plot 1D and 2D arrays with [ImPlot](https://github.com/epezent/implot)

>*Note: ImPlot is a very capable and fast plotting library, not limited to simple 1D and 2D plots. It is available with Fiatlight and ImGui Bundle (on which Fiatlight is based). See [online demo](https://traineq.org/implot_demo/src/implot_demo.html) of ImPlot for more examples.*

Example
-------

```python
from fiatlight.fiat_kits.fiat_array import simple_plot_gui_demo
simple_plot_gui_demo.main()
```


Custom attributes available for SimplePlotGui
---------------------------------------------

Here is a list of all the possible customizations options:

```python
import fiatlight
from fiatlight.fiat_doc import look_at_code  # noqa

%run_bash_command fiatlight gui_info SimplePlotGui
```


Source code for the example
---------------------------

```python
%look_at_python_file fiat_kits/fiat_array/simple_plot_gui_demo.py
```

