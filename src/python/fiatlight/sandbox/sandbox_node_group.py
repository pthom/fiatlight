from imgui_bundle import immapp, imgui_node_editor as ed, imgui_node_editor_ctx as edctx, imgui, ImVec2, ImVec4  # noqa


def gui() -> None:
    ed.begin("Node Editor")

    pin_input_id = ed.PinId(200)
    pin_output_id = ed.PinId(201)
    link_id = ed.LinkId(202)

    with edctx.begin_group_hint(ed.NodeId(20)):
        with edctx.begin_node(ed.NodeId(40)):
            imgui.text("Group Hint")
            ed.group(ImVec2(200, 200))

    with edctx.begin_node(ed.NodeId(1)):
        with edctx.begin_pin(pin_input_id, ed.PinKind.input):
            imgui.text("Pin 200")
        imgui.text("Node 1")

    with edctx.begin_node(ed.NodeId(2)):
        with edctx.begin_pin(pin_output_id, ed.PinKind.output):
            imgui.text("Pin 201")
        imgui.text("Node 2")

    with edctx.begin_node(ed.NodeId(3)):
        imgui.text("Node 3")

    ed.link(link_id, pin_input_id, pin_output_id, ImVec4(1.0, 1.0, 1.0, 1.0), 3.0)
    # ed.flow(link_id, ed.FlowDirection.forward)

    ed.end()


def main() -> None:
    immapp.run(gui, with_node_editor=True)


if __name__ == "__main__":
    main()
