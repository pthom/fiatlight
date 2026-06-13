"""Pure layout algorithms for the Sugiyama-style graph auto-layout.

No imgui / no graph-GUI dependency: these operate on node ids and (src, dst)
edges only, so they are unit-tested in isolation
(`fiat_nodes/tests/test_layered_layout.py`). `FunctionsGraphGui._layout_graph_layered`
feeds them the live graph and turns the result into node positions.

The two phases implemented here:
  * `compute_layered_ranks` - layer assignment (which column each node goes in).
  * `order_layers_to_reduce_crossings` - within-column ordering to untangle links.
Coordinate assignment (turning columns into x/y) stays in the GUI, since it needs
the real node sizes.
"""
from collections import defaultdict
from typing import List, Dict, Tuple


def compute_layered_ranks(order: List[str], edges: List[Tuple[str, str]]) -> Dict[str, int]:
    """Longest-path layering of a DAG (Kahn's algorithm), the layer-assignment
    phase of a Sugiyama layout. `order` lists node ids in stable order; `edges`
    are (src, dst). Returns each node's layer (data-flow depth: sources at 0).
    Edges to/from unknown ids are ignored; nodes caught in a cycle keep layer 0
    (graceful rather than looping forever). Pure - unit-tested."""
    node_set = set(order)
    successors: Dict[str, List[str]] = defaultdict(list)
    in_degree: Dict[str, int] = defaultdict(int)
    for s, d in edges:
        if s in node_set and d in node_set:
            successors[s].append(d)
            in_degree[d] += 1

    layer: Dict[str, int] = {sid: 0 for sid in order}
    remaining = {sid: in_degree[sid] for sid in order}
    queue = [sid for sid in order if remaining[sid] == 0]
    while queue:
        s = queue.pop(0)
        for d in successors[s]:
            if layer[d] < layer[s] + 1:
                layer[d] = layer[s] + 1
            remaining[d] -= 1
            if remaining[d] == 0:
                queue.append(d)
    return layer


def _count_inversions(seq: List[int]) -> int:
    """Number of out-of-order pairs in `seq` (= edge crossings between two layers
    when `seq` is the target positions ordered by source position)."""
    n = len(seq)
    return sum(1 for i in range(n) for j in range(i + 1, n) if seq[i] > seq[j])


def order_layers_to_reduce_crossings(
    order: List[str], edges: List[Tuple[str, str]], layer: Dict[str, int], iterations: int = 4
) -> Dict[int, List[str]]:
    """Crossing-minimization phase of a Sugiyama layout: return, per layer, the
    node order that reduces edge crossings between adjacent layers.

    Uses the barycenter heuristic with iterated down/up sweeps, keeping the
    ordering with the fewest crossings. Only edges between consecutive layers are
    considered (long edges would need dummy nodes - a later refinement); ties
    keep the previous order, so the result is deterministic. Pure - unit-tested."""
    node_set = set(order)
    max_layer = max(layer.values(), default=0)
    adj_edges = [(s, d) for (s, d) in edges if s in node_set and d in node_set and layer[d] == layer[s] + 1]

    preds: Dict[str, List[str]] = defaultdict(list)
    succs: Dict[str, List[str]] = defaultdict(list)
    for s, d in adj_edges:
        succs[s].append(d)
        preds[d].append(s)

    columns: Dict[int, List[str]] = {L: [sid for sid in order if layer[sid] == L] for L in range(max_layer + 1)}

    def positions() -> Dict[str, int]:
        return {sid: i for col in columns.values() for i, sid in enumerate(col)}

    def count_crossings() -> int:
        pos = positions()
        total = 0
        for layer_idx in range(max_layer):
            pairs = sorted((pos[s], pos[d]) for (s, d) in adj_edges if layer[s] == layer_idx)
            total += _count_inversions([d for _, d in pairs])
        return total

    def sweep(layer_idx: int, neighbors: Dict[str, List[str]], ref_pos: Dict[str, int]) -> None:
        # Reorder a layer by the mean position of each node's neighbors in the
        # reference (adjacent) layer; nodes with no neighbor keep their slot.
        keyed = []
        for i, sid in enumerate(columns[layer_idx]):
            ns = neighbors[sid]
            bc = sum(ref_pos[n] for n in ns) / len(ns) if ns else float(i)
            keyed.append((bc, i, sid))
        keyed.sort()
        columns[layer_idx] = [sid for _, _, sid in keyed]

    best = {L: list(col) for L, col in columns.items()}
    best_crossings = count_crossings()
    for _ in range(iterations):
        for layer_idx in range(1, max_layer + 1):
            sweep(layer_idx, preds, positions())
        for layer_idx in range(max_layer - 1, -1, -1):
            sweep(layer_idx, succs, positions())
        crossings = count_crossings()
        if crossings < best_crossings:
            best_crossings = crossings
            best = {L: list(col) for L, col in columns.items()}
    return best
