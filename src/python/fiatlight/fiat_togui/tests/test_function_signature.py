"""
This script is a sandbox to test how the signature of C++ bound functions could be obtained from the stubs.

It uses "makefun" to create a wrapper function with the correct signature.
    https://smarie.github.io/python-makefun/
    pip install makefun

In this example, hello_imgui.image_proportional_size is a C++ function that is bound to Python using pybind11.
Its signature is not available using inspect.signature(), but it is available in the stubs.

"""

from imgui_bundle import hello_imgui, ImVec2
from makefun import create_function
import inspect


def test_hello_imgui_image_proportional_size_signature() -> None:
    # In this example, hello_imgui.image_proportional_size is a C++ function that is bound to Python using pybind11.
    f = hello_imgui.image_proportional_size
    # We cannot inspect its signature
    got_exception = False
    try:
        f_sig = inspect.signature(f)  # noqa
    except Exception as e:
        # This exception will be raised:
        # no signature found for builtin <built-in method image_proportional_size of PyCapsule object at 0x102a45f80>
        print(e)
        got_exception = True
    assert got_exception

    # However, the signature is available in the stubs and looks like this:
    f_sig_str = "image_proportional_size(asked_size: ImVec2, image_size: ImVec2) -> ImVec2"

    # Using makefun, we can create a wrapper function whose signature is the one we want
    f2 = create_function(f_sig_str, f)  # type: ignore
    f2_sig = inspect.signature(f2)
    expected_sig = "(asked_size: imgui_bundle._imgui_bundle.imgui.ImVec2, image_size: imgui_bundle._imgui_bundle.imgui.ImVec2) -> imgui_bundle._imgui_bundle.imgui.ImVec2"
    assert str(f2_sig) == expected_sig

    # Check that the wrapper function works
    asked_size = ImVec2(100, 0)
    image_size = ImVec2(640, 480)
    obtained_size = hello_imgui.image_proportional_size(asked_size, image_size)
    obtained_size2 = f2(asked_size, image_size)
    assert obtained_size.x == obtained_size2.x and obtained_size.y == obtained_size2.y


def test_sorted_signature() -> None:
    # Another test around the signature of the python function "sorted"
    f = sorted

    # sorted is defined as "def sorted(*args, **kwargs): # real signature unknown" in the stubs
    # However, inspect.signature() will return a slightly better signature
    # (which does not include neither param type hints, nor return type hints)
    f_sig = inspect.signature(f)
    assert str(f_sig) == "(iterable, /, *, key=None, reverse=False)"

    #
    # Let's create a better signature for the function
    #
    # First, we need to import the types that we will use in the signature
    from typing import TypeVar, Iterable, Optional, Callable, Any, List  # noqa

    T = TypeVar("T")  # noqa
    # Then we can define the signature as a string
    better_sig = (
        "(iterable: Iterable[T], /, *, key: Optional[Callable[[T], Any]] = None, reverse: bool = False) -> List[T]"
    )

    # Using makefun, we can create a wrapper function whose signature is the one we want
    f2 = create_function(better_sig, f)

    # Check that the signature is now the one we want
    # Note: T is replaced by ~T in the obtained signature
    # This is meant to differentiate TypeVar instances from regular types or classes in the signature
    f2_sig = inspect.signature(f2)
    expected_sig = (
        "(iterable: Iterable[~T], /, *, key: Optional[Callable[[~T], Any]] = None, reverse: bool = False) -> List[~T]"
    )
    assert str(f2_sig) == expected_sig

    # Check that the wrapper function works
    obtained = f2([4, 5, 3, 2, 1], reverse=True)
    assert obtained == [5, 4, 3, 2, 1]


def test_get_function_signature() -> None:
    from fiatlight.fiat_togui.function_signature import get_function_signature

    signature_string = (
        "(iterable: Iterable[T], /, *, key: Optional[Callable[[T], Any]] = None, reverse: bool = False) -> List[T]"
    )
    signatures_import_code = "from typing import Iterable, Optional, Callable, TypeVar; T = TypeVar('T')"  # noqa

    # We can transmit the needed code to import the needed types with `signatures_import_code`
    # In this case, since `get_function_signature` already imports the most common types,
    # and defines T and U as TypeVar instances, we don't need to transmit anything
    sig = get_function_signature(
        sorted,
        signature_string=signature_string,
        # signatures_import_code=signatures_import_code
    )
    # Note: T is replaced by ~T in the obtained signature (this is meant to differentiate TypeVar instances
    # from regular types or classes)
    assert (
        str(sig)
        == "(iterable: Iterable[~T], /, *, key: Optional[Callable[[~T], Any]] = None, reverse: bool = False) -> List[~T]"
    )


def test_wrap_signature_to_gui() -> None:
    import fiatlight

    sorted_gui = fiatlight.FunctionWithGui(
        sorted, signature_string="(words: List[str], /, reverse: bool = False) -> List[str]"
    )

    sorted_gui.input("words").value = ["hello", "world"]
    sorted_gui.input("reverse").value = True
    sorted_gui.invoke()
    obtained = sorted_gui._outputs_with_gui[0].data_with_gui.value
    assert obtained == ["world", "hello"]
