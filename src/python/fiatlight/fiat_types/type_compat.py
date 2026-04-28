"""Link-time type compatibility for fiatlight.

Used by the graph editor to accept or reject a new link between an output pin
of type `output_type` and an input pin of type `input_type`.

Rules (in order):
    1. `Any` on either side accepts anything.
    2. Equal fully-qualified type names accept (short-circuit, also handles
       `Union[A, B] -> Union[A, B]` directly).
    3. If `output_type` is a `Union`, accept only if *every* member matches
       `input_type` (the producer might emit any of them, all must be legal).
       Recursing per-member lets each member be matched against an input Union
       via rule 4 — so `Union[A, B] -> Union[A, B, C]` works.
    4. If `input_type` is a `Union` (incl. `Optional[T]`), accept if `output_type`
       matches *any* member.
    5. NewType supertype walking on the output side: walk
       `output_type.__supertype__` chain — if any link in the chain matches
       `input_type`, accept. (One-directional: `ImageRgb -> ImageU8_3` ok,
       `ImageU8_3 -> ImageRgb` rejected.)
    6. Numpy escape hatch: a *bare* `np.ndarray` annotation on one side accepts
       any image-like NewType (chain ending in `np.ndarray`) on the other side.
       Two NewType image types do NOT auto-match through this rule.
    7. Otherwise reject — the user can add an explicit cast node.
"""

from __future__ import annotations

import types
import typing
from typing import Any, Iterable

import numpy as np

from fiatlight.fiat_types.typename_utils import TypeLike, fully_qualified_typename, base_typename


__all__ = [
    "is_link_compatible",
    "explain_incompatibility",
]


# ---------------------------------------------------------------------------
#  Internal helpers
# ---------------------------------------------------------------------------
def _is_any(t: TypeLike) -> bool:
    return t is Any or t is typing.Any  # type: ignore[comparison-overlap]


def _is_union(t: TypeLike) -> bool:
    origin = typing.get_origin(t)
    return origin is typing.Union or isinstance(t, types.UnionType)


def _union_members(t: TypeLike) -> tuple[TypeLike, ...]:
    return typing.get_args(t)  # type: ignore[no-any-return]


def _is_newtype(t: TypeLike) -> bool:
    return hasattr(t, "__supertype__")


def _supertype_chain(t: TypeLike) -> Iterable[TypeLike]:
    """Yield t, then t.__supertype__, then its supertype, etc.

    Stops as soon as a non-NewType is reached (which is itself yielded last).
    """
    seen: set[int] = set()
    cur: TypeLike = t
    while True:
        if id(cur) in seen:  # pathological loop guard
            return
        seen.add(id(cur))
        yield cur
        if not _is_newtype(cur):
            return
        cur = cur.__supertype__  # type: ignore[union-attr]


def _typename_eq(a: TypeLike, b: TypeLike) -> bool:
    if a is b:
        return True
    try:
        return fully_qualified_typename(a) == fully_qualified_typename(b)
    except Exception:
        return False


def _is_bare_numpy(t: TypeLike) -> bool:
    """True iff `t` is `np.ndarray` (possibly parameterised) and NOT a NewType."""
    if _is_newtype(t):
        return False
    if t is np.ndarray:
        return True
    return typing.get_origin(t) is np.ndarray


def _reaches_numpy(t: TypeLike) -> bool:
    """True iff walking the supertype chain of `t` reaches `np.ndarray`."""
    for link in _supertype_chain(t):
        if link is np.ndarray or typing.get_origin(link) is np.ndarray:
            return True
    return False


# ---------------------------------------------------------------------------
#  Public API
# ---------------------------------------------------------------------------
def is_link_compatible(output_type: TypeLike, input_type: TypeLike) -> bool:
    """Return True if a value of `output_type` can be linked into an input
    annotated `input_type`.  See module docstring for the rules.
    """
    # 1. Any
    if _is_any(input_type) or _is_any(output_type):
        return True

    # 2. Same type (short-circuit; also handles Union == Union)
    if _typename_eq(output_type, input_type):
        return True

    # 3. Union on output: accept only if every member matches.
    # We recurse per-member so each member can still be matched against an
    # input Union via rule 4 (e.g. Union[A,B] -> Union[A,B,C] is accepted).
    if _is_union(output_type):
        members = _union_members(output_type)
        if len(members) == 0:
            return False
        return all(is_link_compatible(m, input_type) for m in members)

    # 4. Union on input: accept if any member matches
    if _is_union(input_type):
        return any(is_link_compatible(output_type, m) for m in _union_members(input_type))

    # 5. NewType supertype walking (output side only)
    for link in _supertype_chain(output_type):
        if link is output_type:
            continue  # already handled by rule 4
        if _typename_eq(link, input_type):
            return True
        # The intermediate link itself may be a Union (e.g. ImageU8_WithNbChannels),
        # in which case we let the recursion check it.
        if _is_union(link):
            if is_link_compatible(link, input_type):
                return True

    # 6. Numpy bare-ndarray escape hatch
    if _is_bare_numpy(output_type) and _reaches_numpy(input_type):
        return True
    if _is_bare_numpy(input_type) and _reaches_numpy(output_type):
        return True

    return False


def explain_incompatibility(output_type: TypeLike, input_type: TypeLike) -> str:
    """Human-readable reason why this link is rejected (used as a tooltip).

    Returns the empty string if the link is compatible.
    """
    if is_link_compatible(output_type, input_type):
        return ""
    return f"Cannot link: output is {base_typename(output_type)}, input expects {base_typename(input_type)}"
