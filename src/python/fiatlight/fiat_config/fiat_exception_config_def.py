class FiatExceptionConfig:
    _break_on_exception: bool = False

    def __init__(self) -> None:
        self._break_on_exception = False

    def shall_break(self) -> bool:
        return self._break_on_exception

    def break_on(self) -> None:
        self._break_on_exception = True

    def break_off(self) -> None:
        self._break_on_exception = False
