from fiatlight.fiat_kits.fiat_array.simple_plot_gui import SimplePlotType, SimplePlotParams, SimplePlotGui


def test_plot_type() -> None:
    t = SimplePlotType.bars
    assert t.name == "bars"

    assert SimplePlotType.from_str("scatter") == SimplePlotType.scatter


def test_serialize_params() -> None:
    params = SimplePlotParams()
    array_with_gui = SimplePlotGui(params)
    as_dict = array_with_gui.save_gui_options_to_json()
    assert as_dict["_plot_type_str"] == "line"

    as_dict["_plot_type_str"] = "bars"
    array_with_gui.load_gui_options_from_json(as_dict)
    assert array_with_gui.plot_presenter.plot_params._plot_type_str == "bars"
