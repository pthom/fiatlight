class FiatToGuiException(Exception):
    """Exception raised when an error occurs in the Fiat to GUI conversion (and only in this case).

    This exception tries to help the user by providing context information about the error
    (like the current function being transformed, the current type, etc.).
    """

    def __init__(self, message: str) -> None:
        # Yes, there is a dependency smell here...
        from fiatlight.fiat_togui.to_gui_context import to_gui_context_info

        message = message + "\n\n" + to_gui_context_info()
        super().__init__(message)
