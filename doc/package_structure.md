

# Core of Fiatlight framework

```
src/python/fiatlight/
├── __init__.py
│
├── fiat_core                        # Core of the framework
│     ├── __init__.py
│     ├── any_data_with_gui.py       # able to add Gui to any data
│     ├── any_data_gui_callbacks.py  # callbacks for any_data_with_gui (provide Gui functions)
│     ├── function_with_gui.py       # able to add Gui to any function (by presenting its inputs and outputs)
│     ├── functions_graph.py         # a graph of functions
│     ├── output_with_gui.py         # wrapper around AnyDataWithGui for function outputs
│     ├── param_with_gui.py          # wrapper around AnyDataWithGui for function parameters
│     ├── composite_gui.py           # creates Gui for Optional, Enum, List, etc
│     ├── fiat_exception.py
│     ├── function_node.py           # a node in the functions graph (can invoke a function)
│     ├── function_signature.py
│     ├── primitives_gui.py          # creates Gui for primitives (int, float, str, etc)
│     └── to_gui.py                  # able to transform any function to a function with Gui
│                                    #   (by parsing its signature)
│
├── fiat_nodes
│     ├── __init__.py
│     ├── function_node_gui.py          # Gui for function_node
│     ├── functions_graph_gui.py        # Gui for functions_graph
│
├── fiat_runner
│     ├── __init__.py                   # Provides fiatlight.fiat_run(fn), fiat_run_composition([fns]), etc.
│     ├── fiat_gui.py
│     └── functions_collection.py       # a collection of functions that can be added interactively to the functions graph
│
├── fiat_config                         # Style and configuration of the framework
│     ├── __init__.py
│     ├── fiat_config_def.py
│     ├── fiat_exception_config_def.py
│     └── fiat_style_def.py
│
├── fiat_types                          # Strongly typed data types that enable the framework
│     ├── __init__.py                   #    to create a GUI automatically for them
│     ├── fiat_number_types.py          # Float0_1, Float0_100, Int0_100, etc
│     └── str_types.py                  # ImagePath, TextPath, Prompt, etc
│     ├── base_types.py
│     ├── function_types.py             # VoidFunction, BoolFunction, etc
│     ├── color_types.py
│     ├── error_types.py
│
├── fiat_utils
│     ├── __init__.py
│     ├── fiat_math.py
│     ├── functional_utils.py
│     ├── lazy_module.py
│     └── registry.py
│
├── fiat_widgets
│     ├── __init__.py
│     ├── fiat_osd.py
│     ├── float_widgets.py
│     ├── fontawesome6_ctx_utils.py
│     ├── group_panel.py
│     ├── imgui.ini
│     ├── misc_widgets.py
│     ├── node_separator.py
│     └── ribbon_panel.py
│
```

# Specialized modules and presenters per data type:
```
├── fiat_array
│     ├── __init__.py
│     ├── array_types.py         # FloatMatrix_Dim1, FloatMatrix_Dim2, IntMatrix_Dim1, etc
│     └── simple_plot_gui.py     # Can present FloatMatrix_Dim1 & FloatMatrix_Dim2 as a plot
│
├── fiat_audio
│     ├── __init__.py
│     ├── audio_functions.py
│     ├── audio_record_gui.py
│     ├── sound_wave.py
│     ├── sound_wave_gui.py
│     └── sound_wave_player.py
├── fiat_image
│     ├── __init__.py
│     ├── cv_color_type.py
│     ├── cv_color_type_gui.py
│     ├── image_gui.py
│     ├── image_types.py
│     ├── lut.py
│     └── lut_gui.py
├── py.typed

```
