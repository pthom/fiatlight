_IS_RENDERING_IN_NODE: bool = False


def is_rendering_in_node() -> bool:
    """Check if we are currently rendering inside a Node.

    You may want to check this value when implementing `present` or `edit`
    callbacks inside `AnyDataGuiCallbacks` for several possible reasons:

        - Some widgets cannot be presented in a Node (e.g., a multiline text input),
          be can be presented in a detached window.
        - When inside a Node, you may want to render a smaller version, to save space
          (as opposed to rendering a larger version in a detached window).
    """
    return _IS_RENDERING_IN_NODE
