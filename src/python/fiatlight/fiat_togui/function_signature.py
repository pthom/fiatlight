from fiatlight.fiat_core.togui_exception import FiatToGuiException
from typing import Callable, Any
import inspect


def get_function_signature(
    f: Callable[..., Any],
    *,
    signature_string: str | None = None,
) -> inspect.Signature:
    """get_function_signature is an improved version of inspect.signature.
    By default, it uses inspect.signature() to get the signature of a function.

    :param f: the function for which we want to get the signature
    :param signature_string: a string representing the signature of the function
    :return: the signature of the function

    inspect.signature():
        - works well for functions that have type annotations
        - may fail on some native functions: for example, with the function `cv2.GaussianBlur`, it raises a ValueError
        - may return an insufficient signature for some functions: for example, with the function `sorted`, it returns
            `"(iterable, /, *, key=None, reverse=False)"` which is not very informative.

    get_function_signature() can be used to try to get a better signature.
    For example, we can use it to get a better signature for the function `sorted`:
    See this extract from test_function_signature:

        def test_get_function_signature():
            from fiatlight.core.function_signature import get_function_signature

            signature_string = "(iterable: Iterable[T], /, *, key: Optional[Callable[[T], Any]] = None, reverse: bool = False) -> List[T]"
            signatures_import_code = "from typing import Iterable, Optional, Callable, TypeVar; T = TypeVar('T')"

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
            assert str(sig) == "(iterable: Iterable[~T], /, *, key: Optional[Callable[[~T], Any]] = None, reverse: bool = False) -> List[~T]"

    Note: for more details about this function, see this ChatGPT discussion:
        https://chat.openai.com/share/2594b2c8-1de2-441a-902a-ad6bf6071faf
    """

    # Import the most common types and define T and U as TypeVar instances,
    # so that they can be used in the signature_string without having to import them manually
    # via signatures_import_code. (add noqa comments to avoid "unused import" warnings)
    from typing import List, Any, Callable, Optional, TypeVar, Iterable, Tuple, Set, Sequence, Mapping, Union  # noqa

    T = TypeVar("T")  # noqa
    U = TypeVar("U")  # noqa

    if signature_string is not None:
        from makefun import create_function

        def foo() -> None:
            pass

        f_new_sig = create_function(signature_string, foo)  # type: ignore
        sig = inspect.signature(f_new_sig)
    else:
        try:
            sig = inspect.signature(f)
        except ValueError as e:
            raise FiatToGuiException(f"Function {f.__name__} has no type annotations") from e
    return sig
