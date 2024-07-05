fiat_dataframe: pandas DataFrame explorer
=========================================

Fiatlight provides `DataFrameWithGui`, a viewer for pandas dataframes that allows to sort, and visualize the data.
Composed with the advanced GUI creation capabilities of fiatlight, it can also filter data.

Example
-------

```python
from fiatlight.fiat_kits.fiat_dataframe import dataframe_with_gui_demo_titanic
dataframe_with_gui_demo_titanic.main()
```

By clicking on the magnifier button ![popup_button.png](_static/images/popup_button.png) on top of the dataframe, you can open it in a popup where sorting options are available. Click on one column (or shift-click on multiple columns) to sort the data.

```
dataframe_with_gui_demo_titanic.main()
```


Fiat attributes available for DataFrameWithGui
------------------------------------------------

Here is a list of all the possible customizations options:

```
%%bash
fiatlight gui DataFrameWithGui
```


Source code for the example
---------------------------

```python
import fiatlight
from fiatlight.fiat_notebook import look_at_code  # noqa
%look_at_python_file fiat_kits/fiat_dataframe/dataframe_with_gui_demo_titanic.py
```

