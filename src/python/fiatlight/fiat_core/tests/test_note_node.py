"""Tests for the editable NoteNode: its text is a serializable param, so it survives the
copy/paste round-trip (serialize_nodes -> instantiate_nodes)."""

from fiatlight.fiat_core.functions_graph import FunctionsGraph
from fiatlight.fiat_core.function_with_gui import FunctionWithGui
from fiatlight.fiat_core.note_node import NoteNode


def _factory(ref: str) -> FunctionWithGui:
    note = NoteNode()
    if note.function_ref == ref:
        return note
    raise ValueError(f"unknown ref {ref}")


def test_note_text_survives_copy_paste() -> None:
    g = FunctionsGraph()
    n = g.add_function(NoteNode("# Title\n\nbody **bold**"))

    payload = g.serialize_nodes([n])
    created = g.instantiate_nodes(payload, _factory)

    assert len(created) == 1
    new_note = created[0][1].function_with_gui
    assert isinstance(new_note, NoteNode)
    assert new_note.note_params.md_string == "# Title\n\nbody **bold**"


def test_note_text_and_width_survive_workspace_save_load() -> None:
    """Both the markdown text and the (editable) width persist through the workspace round-trip."""
    g = FunctionsGraph()
    g.add_function(NoteNode("hello **world**", text_width_em=42.0))
    core = g.save_workspace_core_to_json()

    g2 = FunctionsGraph()
    g2.load_workspace_core_from_json(core, _factory)

    note = g2.functions_nodes[0].function_with_gui
    assert isinstance(note, NoteNode)
    assert note.note_params.md_string == "hello **world**"
    assert note.note_params.text_width_em == 42.0


def test_default_note_is_empty() -> None:
    note = NoteNode()
    assert note.note_params.md_string == ""
    assert note.function_name == "Note"
