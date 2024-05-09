```
tree -F -I "__pycache__|*json|*ini|doc|demos|sandbox|tests" src/python
```


```
src/python/
└── fiatlight/
    ├── __init__.py
    ├── fiat_core/
    │     ├── __init__.py
    │     ├── any_data_gui_callbacks.py
    │     ├── any_data_with_gui.py
    │     ├── function_node.py
    │     ├── function_with_gui.py
    │     ├── functions_graph.py
    │     ├── output_with_gui.py
    │     └── param_with_gui.py
    ├── fiat_togui/
    │     ├── __init__.py
    │     ├── composite_gui.py
    │     ├── explained_value_gui.py
    │     ├── function_signature.py
    │     ├── primitives_gui.py
    │     └── to_gui.py
    ├── fiat_types/
    │     ├── __init__.py
    │     ├── base_types.py
    │     ├── color_types.py
    │     ├── error_types.py
    │     ├── fiat_exception.py
    │     ├── fiat_number_types.py
    │     ├── function_types.py
    │     └── str_types.py
    ├── fiat_config/
    │     ├── __init__.py
    │     ├── fiat_config_def.py
    │     ├── fiat_exception_config_def.py
    │     └── fiat_style_def.py
    ├── fiat_nodes/
    │     ├── __init__.py
    │     ├── function_node_gui.py
    │     └── functions_graph_gui.py
    ├── fiat_runner/
    │     ├── __init__.py
    │     ├── fiat_gui.py
    │     └── functions_collection.py
    ├── fiat_utils/
    │     ├── __init__.py
    │     ├── fiat_math.py
    │     ├── functional_utils.py
    │     ├── lazy_module.py
    │     ├── print_repeatable_message.py
    │     └── registry.py
    ├── fiat_widgets/
    │     ├── __init__.py
    │     ├── fiat_osd.py
    │     ├── float_widgets.py
    │     ├── fontawesome6_ctx_utils.py
    │     ├── group_panel.py
    │     ├── mini_buttons.py
    │     ├── misc_widgets.py
    │     ├── node_separator.py
    │     └── ribbon_panel.py
    │
    │
    ├── fiat_kits/
    │     ├── __init__.py
    │     ├── fiat_array/
    │     │     ├── __init__.py
    │     │     ├── array_types.py
    │     │     └── simple_plot_gui.py
    │     ├── fiat_audio/
    │     │     ├── __init__.py
    │     │     ├── audio_functions.py
    │     │     ├── audio_record_gui_old.py
    │     │     ├── audio_types.py
    │     │     ├── audio_types_gui.py
    │     │     ├── microphone_gui.py
    │     │     ├── microphone_io.py
    │     │     ├── sound_wave_player.py
    │     │     ├── sound_wave_player_gui.py
    │     │     ├── sound_wave_recorder.py
    │     │     ├── wip_audio_provider.py
    │     │     ├── wip_audio_provider_gui.py
    │     │     ├── wip_audio_recorder_gui.py
    │     │     └── wip_microphone_gui.py
    │     └── fiat_image/
    │         ├── __init__.py
    │         ├── cv_color_type.py
    │         ├── cv_color_type_gui.py
    │         ├── image_gui.py
    │         ├── image_types.py
    │         ├── lut.py
    │         └── lut_gui.py

```
