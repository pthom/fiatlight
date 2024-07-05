fiat_implot: widget for 1D and 2D numpy arrays
=============================================

Fiatlight provides `SimplePlotGui`, a viewer for numpy arrays that allows to plot 1D and 2D arrays with [ImPlot](https://github.com/epezent/implot)

> * ImPlot is a very capable and fast plotting library, not limited to simple 1D and 2D plots. It is available with Fiatlight and ImGui Bundle (on which Fiatlight is based). See [online demo](https://traineq.org/implot_demo/src/implot_demo.html) of ImPlot for more examples.
> * It is faster than Matplotlib within Fiatlight, and well adapted for real time plots (can refresh at 120FPS +)

Example
-------

```python
from fiatlight.fiat_kits.fiat_implot import demo_implot

demo_implot.main()
```


Fiat attributes available for SimplePlotGui
---------------------------------------------

**Here is a list of all the type handled by SimplePlotGui:**

```
%%bash
fiatlight types FloatMatrix_Dim
```


**Here is a list of all the possible customizations options:**

```
%%bash
fiatlight gui SimplePlotGui
```


Source code for the example
---------------------------

```python
import fiatlight
from fiatlight.fiat_notebook import look_at_code  # noqa
%look_at_python_file fiat_kits/fiat_implot/demo_implot.py
```

