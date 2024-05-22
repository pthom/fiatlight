import nbformat
from nbformat import NotebookNode
import re
import os
from typing import List
from fiatlight.fiat_doc import code_utils
from dataclasses import dataclass


THIS_DIR = os.path.dirname(__file__)
DOC_DIR = os.path.abspath(f"{THIS_DIR}/../doc")


@dataclass
class _WrappedString:
    value: str


@dataclass
class _CompositeMarkdown(_WrappedString):
    pass


@dataclass
class _Markdown(_WrappedString):
    pass


@dataclass
class _Code(_WrappedString):
    pass


class _NotebookContent:
    items: List[_Markdown | _Code]

    def __init__(self) -> None:
        self.items = []


def _md_to_notebook_content(md_string: _CompositeMarkdown) -> _NotebookContent:
    md_string = _CompositeMarkdown(code_utils.unindent_code(md_string.value))
    # Create a new notebook
    notebook_content = _NotebookContent()

    # Regular expression to match code blocks
    code_block_re = re.compile(r"```python(.*?)```", re.DOTALL)

    # Split the Markdown string into parts, separating code blocks and Markdown
    parts = code_block_re.split(md_string.value)

    for i, part in enumerate(parts):
        part = code_utils.unindent_code(part)
        is_code = i % 2 == 1
        if is_code:
            notebook_content.items.append(_Code(part))
        else:
            notebook_content.items.append(_Markdown(part))

    return notebook_content


def _md_to_notebook(md_string: _CompositeMarkdown) -> NotebookNode:
    notebook_content = _md_to_notebook_content(md_string)

    # Create a new notebook
    nb: NotebookNode = nbformat.v4.new_notebook()  # type: ignore
    for item in notebook_content.items:
        if isinstance(item, _Markdown):
            nb.cells.append(nbformat.v4.new_markdown_cell(item.value))  # type: ignore
        else:
            nb.cells.append(nbformat.v4.new_code_cell(item.value))  # type: ignore

    return nb


def _update_notebook_code_cells(notebook: NotebookNode, md_string: _CompositeMarkdown) -> None:
    notebook_content = _md_to_notebook_content(md_string)
    if len(notebook_content.items) != len(notebook.cells):
        raise ValueError("The number of cells in the notebook and in the Markdown string do not match.")

    for i, item in enumerate(notebook_content.items):
        if isinstance(item, _Code):
            notebook.cells[i].source = item.value


def _function_or_class_to_notebook(obj: object, notebook_to_update: NotebookNode | None = None) -> NotebookNode:
    if obj.__doc__ is None:
        raise ValueError(f"{obj} does not have a docstring.")
    docstring = _CompositeMarkdown(obj.__doc__)
    # Remove first line from the docstring (which is a summary, not intended for the notebook)
    docstring = docstring.split("\n", 1)[1]  # type: ignore
    if notebook_to_update is None:
        notebook = _md_to_notebook(docstring)
    else:
        notebook = notebook_to_update
        _update_notebook_code_cells(notebook, docstring)
    return notebook


def save_function_or_class_doc_to_notebook(obj: object, update_existing: bool, filename: str | None = None) -> None:
    if filename is None:
        if not hasattr(obj, "__name__"):
            raise ValueError(f"{obj} does not have a name.")
        filename = f"{DOC_DIR}/{obj.__name__}.ipynb"

    previous_notebook: NotebookNode | None = None
    if update_existing:
        with open(filename) as f:
            previous_notebook = nbformat.read(f, as_version=4)  # type: ignore

    new_notebook = _function_or_class_to_notebook(obj, previous_notebook)
    with open(filename, "w") as f:
        nbformat.write(new_notebook, f)  # type: ignore
