from imgui_bundle import imgui, hello_imgui, portable_file_dialogs as pfd


msg: pfd.message | None = None
notif: pfd.notify | None = None


def gui() -> None:
    global msg, notif
    if imgui.button("Add Notif"):
        pfd.notify("Hello", "World", pfd.icon.error)
    if imgui.button("Add message"):
        msg = pfd.message("Hello", "World", pfd.choice.yes_no_cancel, pfd.icon.warning)
    if msg is not None and msg.ready():
        print("msg ready: " + str(msg.result()))
        msg = None


def main() -> None:
    hello_imgui.run(gui)


if __name__ == "__main__":
    main()
