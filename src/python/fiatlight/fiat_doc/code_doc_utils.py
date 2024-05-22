import inspect
from dataclasses import dataclass
from typing import List

from fiatlight.fiat_doc import code_utils


def make_class_header__abandoned(
    class_: object, include_private_attributes: bool, include_private_methods: bool
) -> str:
    """Create the equivalent of a C header file from a class object.

    ABANDONED ATTEMPT: This function is not functional!!!

    The returned string should be computed by:
        - extracting the source code of the class
        - including all attributes (public, and private if include_private_attributes is True), together with doc
        - including all methods (public, and private if include_private_methods is True), together with doc, but where the
        code is replaced by "..."
    """
    class_source = inspect.getsource(class_)  # type: ignore
    class_source = code_utils.unindent_code(class_source, flag_strip_empty_lines=True)
    source_lines = class_source.split("\n")

    # class_inner_indent: the indentation of the class body
    # TODO / Later: implement a way to compute the inner indent
    class_inner_indent = " " * 4

    # =================
    # Utility functions
    # =================
    def get_nb_parentheses_this_line(line: str) -> int:
        r = line.count("(") - line.count(")")
        return r

    def is_aligned_with_class_inner_indent(line: str) -> bool:
        has_sufficient_spaces = line.startswith(class_inner_indent)
        does_not_have_more_spaces = not line.startswith(class_inner_indent + " ") and not line.startswith(
            class_inner_indent + "\t"
        )
        return has_sufficient_spaces and does_not_have_more_spaces

    def is_method_def_start(line: str) -> bool:
        """Check if the line is the start of a method definition."""
        looks_like_method_def = line.strip().startswith("def ") and is_aligned_with_class_inner_indent(line)
        return looks_like_method_def

    def is_method_def_on_one_line(line: str) -> bool:
        if not is_method_def_start(line):
            return False
        nb_parentheses_this_line = get_nb_parentheses_this_line(line)
        return nb_parentheses_this_line == 0

    def is_method_def_several_lines(line: str) -> bool:
        if not is_method_def_start(line):
            return False
        nb_parentheses_this_line = get_nb_parentheses_this_line(line)
        return nb_parentheses_this_line > 0

    def is_method_def_end(line: str, current_nb_parentheses: int) -> bool:
        """Check if the line is the end of a method definition.
        Since a method definition might be written on several lines, we need to look for balanced parentheses."""
        nb_parentheses_this_line = get_nb_parentheses_this_line(line)
        current_nb_parentheses += nb_parentheses_this_line
        return current_nb_parentheses == 0

    # =================
    # Start parsing
    # =================
    # lines that will be included in the header
    header_lines: List[str]  # The lines of the header

    # Status of the parser
    @dataclass
    class ParserStatus:
        nb_parentheses: int = 0  # The number of parentheses in the current line
        is_inside_method_signature: bool = False  # Whether we are currently parsing a method signature
        is_inside_method_body: bool = False  # Whether we are currently parsing a method body
        was_ellipsis_added: bool = False  # Whether we have already added "..." for the method body

    parser_status = ParserStatus()
    header_lines = []

    for line in source_lines:
        if is_method_def_on_one_line(line):
            header_lines.append(line)
        elif is_method_def_several_lines(line):
            header_lines.append(line)
            parser_status.is_inside_method_signature = True
            assert parser_status.nb_parentheses == 0
            parser_status.nb_parentheses += get_nb_parentheses_this_line(line)
        elif parser_status.is_inside_method_signature:
            if is_method_def_end(line, parser_status.nb_parentheses):
                parser_status.is_inside_method_signature = False
                parser_status.is_inside_method_body = True

            header_lines.append(line)  # we shall append the signature
            parser_status.nb_parentheses += get_nb_parentheses_this_line(line)
        elif parser_status.is_inside_method_body:
            if not parser_status.was_ellipsis_added:
                header_lines.append("    ...")
                parser_status.was_ellipsis_added = True
            if is_aligned_with_class_inner_indent(line):
                parser_status.is_inside_method_body = False

            parser_status.nb_parentheses += get_nb_parentheses_this_line(line)
        else:
            header_lines.append(line)
            parser_status.nb_parentheses += get_nb_parentheses_this_line(line)

    r = "\n".join(header_lines)
    return r


def test_make_class_header() -> None:
    class MyClass:
        """This is a class."""

        # This is the attribute x
        x: int = 0

        # This is a private attribute
        _priv_attr: bool = False

        def __init__(self) -> None:
            """This is the constructor."""
            pass

        def public_method(
            self,
            abracabra_abracabra_abracabra_abracabra_: int,
            abracabra_abracabra_abracabra_abracabra_abracabra_abracabra_a: float,
        ) -> None:
            """This is a public method."""
            pass

        def _private_method(self) -> None:
            """This is a private method."""
            pass

    _expected = '''
    class MyClass:
        x: int = 0
        # This is the attribute x

        _priv_attr: bool = False
        # This is a private attribute

        def __init__(self) -> None:
            """This is the constructor."""
            ...

        def public_method(self) -> None:
            """This is a public method."""
            ...

        def _private_method(self) -> None:
            """This is a private method."""
            ...
    '''
    result = make_class_header__abandoned(MyClass, include_private_attributes=True, include_private_methods=True)

    # code_utils.assert_are_codes_equal(result, expected)
    print(result)
