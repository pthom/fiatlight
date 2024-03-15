from imgui_bundle import imgui, immapp, ImVec2, imgui_node_editor as ed


node_id = ed.NodeId(1)
s2 = "After Spring"


def gui() -> None:
    global s2
    ed.begin("ed")
    ed.begin_node(node_id)

    layout_size = ImVec2(ed.get_node_size(node_id).x - 16, 100)

    # imgui.dummy(ImVec2(50, 10))
    imgui.begin_vertical("aaa")
    imgui.text("")
    imgui.begin_horizontal("layout", size=layout_size, align=0.5)
    imgui.text("ABCDEF")
    imgui.spring()
    imgui.text(s2)
    imgui.end_horizontal()
    imgui.end_vertical()

    if imgui.button("+"):
        s2 += "AVDGGDFGDFD"
    if imgui.button("-"):
        s2 = "ABC"

    ed.end_node()
    ed.end()


immapp.run(gui, with_node_editor=True)
