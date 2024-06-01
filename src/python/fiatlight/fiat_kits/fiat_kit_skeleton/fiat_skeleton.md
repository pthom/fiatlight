How to create a fully customizable new widget.
=============================================

fiat_kit_skeleton
-----------------

[fiatlight.fiat_kits.fiat_skeleton](https://github.com/pthom/fiatlight/tree/refact_io/src/python/fiatlight/fiat_kits/fiat_kit_skeleton) is a starting point for creating new widgets: it is a minimalistic kit that contains the necessary files to create a new widget.

```
fiat_kit_skeleton
├── __init__.py
├── mydata.py                      # An example data or library that you want to present
├── mydata_presenter.py            # The presenter of the data
|                                  # Also contains a derivate of PossibleCustomAttributes
|                                  # where all the custom attributes are defined
|
└── mydata_with_gui.py             # MyDataWithGui: the widget that will be displayed in the GUI
                                   # (inherits from AnyDataWithGui, implements all the callbacks
                                   #  of AnyDataGuiCallbacks, and uses MyDataPresenter for
                                   # complex data presentation)
```

See files:
* [mydata.py](https://github.com/pthom/fiatlight/tree/refact_io/src/python/fiatlight/fiat_kits/fiat_kit_skeleton/mydata.py)
* [mydata_presenter.py](https://github.com/pthom/fiatlight/tree/refact_io/src/python/fiatlight/fiat_kits/fiat_kit_skeleton/mydata_presenter.py)
* [mydata_with_gui.py](https://github.com/pthom/fiatlight/tree/refact_io/src/python/fiatlight/fiat_kits/fiat_kit_skeleton/mydata_with_gui.py)


fiat_kit_skeleton in action
---------------------------

[fiatlight.fiat_kits.fiat_dataframe](https://github.com/pthom/fiatlight/tree/refact_io/src/python/fiatlight/fiat_kits/fiat_dataframe) it was developed starting from the skeleton. It is a good example on how it can be customized.

```
fiat_dataframe
├── dataframe_presenter.py                  # The presenter of the data (presentation code)
|                                           # Also contains a derivate of PossibleCustomAttributes
|
├── dataframe_with_gui.py                   # The widget that will be displayed in the GUI
|                                           # (inherits from AnyDataWithGui, implements all the callbacks
|                                          #  of AnyDataGuiCallbacks, and uses DataFramePresenter for
|                                          # complex data presentation)
```

See files:

* [dataframe_presenter.py](https://github.com/pthom/fiatlight/tree/refact_io/src/python/fiatlight/fiat_kits/fiat_dataframe/dataframe_presenter.py)
* [dataframe_with_gui.py](https://github.com/pthom/fiatlight/tree/refact_io/src/python/fiatlight/fiat_kits/fiat_dataframe/dataframe_with_gui.py)

