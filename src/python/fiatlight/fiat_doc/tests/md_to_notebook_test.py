from fiatlight.fiat_doc import notebook_utils
from fiatlight.fiat_doc import code_utils
import nbformat  # noqa


def test_md_to_notebook() -> None:
    md_string = notebook_utils._CompositeMarkdown(
        """
    FunctionWithGui: add GUI to a function
    ========================================
    Introduction
    ------------

    `FunctionWithGui` is ... blah blah ...

        ```python
        import fiatlight as ft
        def foo(a: int, b: float) -> float:
            return a + b
        ft.fiat_run(foo)
        ```

    ### Manual creation example:
    ...Blah blah...

        ```python
        import fiatlight as ft
        def blah(a: int) -> int:
            return a * 2
        ```
    """
    )

    notebook = notebook_utils._md_to_notebook(md_string)

    assert notebook.cells[0].cell_type == "markdown"
    code_utils.assert_are_codes_equal(
        notebook.cells[0].source,
        """
        FunctionWithGui: add GUI to a function
        ========================================
        Introduction
        ------------

        `FunctionWithGui` is ... blah blah ...
        """,
    )

    assert notebook.cells[1].cell_type == "code"
    code_utils.assert_are_codes_equal(
        notebook.cells[1].source,
        """
        import fiatlight as ft
        def foo(a: int, b: float) -> float:
            return a + b
        ft.fiat_run(foo)
            """,
    )
