import fiatlight as fl


def usability_dataclass_no_ctor() -> None:
    class Inner:
        """Inner class with no default constructor.
        It is also not serializable (reloading will display an error at startup)
        """

        x: int

        def __init__(self, x: int):
            self.x = x

        def __str__(self) -> str:
            return f"Inner(x={self.x})"

    @fl.dataclass_with_gui_registration()
    class MyData:
        inner: Inner

    def f(param: MyData) -> MyData:
        return param

    f_gui = fl.FunctionWithGui(f)

    # If you comment out the following line, the application will raise an exception
    # when you try to create an instance.
    f_gui.param_gui("param").callbacks.default_value_provider = lambda: MyData(Inner(42))  # type: ignore

    fl.run(f_gui, app_name="usability_dataclass_no_ctor")


def usability_dataclass_no_ctor_but_registered_types() -> None:
    """Here, MyData is a class with no default constructor.
    However, "int" is a registered type with a default_value_provider (0)
    The application should behave as if there were a default constructor.
    """

    from pydantic import BaseModel

    @fl.base_model_with_gui_registration()
    class MyData(BaseModel):
        x: int

    def f(param: MyData) -> MyData:
        return param

    fl.run(f, app_name="usability_no_ctor_but_registered_types")


if __name__ == "__main__":
    usability_dataclass_no_ctor()
    # usability_dataclass_no_ctor_but_registered_types()
