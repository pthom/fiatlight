import ast
import inspect
from typing import Any
from fiatlight.fiat_doc import code_utils


class MethodBodyRemover(ast.NodeTransformer):
    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.FunctionDef:
        # Remove the method body while keeping the docstring
        if node.body and isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Str):
            # The first statement is a docstring
            docstring_node = node.body[0]
            node.body = [docstring_node, ast.Pass()]
        else:
            node.body = [ast.Pass()]
        return node


def make_class_header(class_: Any) -> str:
    # Get the original source code lines
    original_lines = inspect.getsourcelines(class_)[0]
    class_source = "".join(original_lines)
    from fiatlight.fiat_doc import code_utils

    class_source = code_utils.unindent_code(class_source, flag_strip_empty_lines=True)

    # Parse the class source code into an AST
    tree = ast.parse(class_source)

    # Transform the AST to remove method bodies
    transformer = MethodBodyRemover()
    transformed_tree = transformer.visit(tree)

    # Unparse the modified AST back into source code
    modified_class_source = ast.unparse(transformed_tree)

    return modified_class_source


def test_make_class_header() -> None:
    class MyClass:
        """This is a class.
        Attributes:
            x: int = 0
            _priv_attr: bool = False
        """

        x: int = 0
        _priv_attr: bool = False

        def __init__(self) -> None:
            """This is the constructor."""
            pass

        def public_method(
            self, argument_number1: int, argument_number2: float, argument_number3: str, argument_number4: bool
        ) -> None:
            print(argument_number1)

        def _private_method(self) -> None:
            """This is a private method."""
            print("private method")

    class_header = make_class_header(MyClass)
    # print(class_header)

    code_utils.assert_are_codes_equal(
        class_header,
        '''
    class MyClass:
        """This is a class.
        Attributes:
            x: int = 0
            _priv_attr: bool = False
        """
        x: int = 0
        _priv_attr: bool = False

        def __init__(self) -> None:
            """This is the constructor."""
            pass

        def public_method(self, argument_number1: int, argument_number2: float, argument_number3: str, argument_number4: bool) -> None:
            pass

        def _private_method(self) -> None:
            """This is a private method."""
            pass

    ''',
    )
