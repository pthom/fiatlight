from fiatlight.fiat_nodes.node_group_gui import NodeGroup


def test_node_group_json_round_trip() -> None:
    group = NodeGroup(title="Pre-process", color=(0.1, 0.2, 0.3), position=(12.0, 34.0), size=(300.0, 200.0))
    restored = NodeGroup.from_json(group.to_json())
    assert restored == group


def test_node_group_from_json_defaults() -> None:
    # Missing keys fall back to sane defaults (no crash on partial / legacy data).
    group = NodeGroup.from_json({})
    assert group.title == "Group"
    assert len(group.color) == 3
    assert group.position == (0.0, 0.0)
    assert group.size == (260.0, 180.0)
