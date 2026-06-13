"""Manual smoke test for Reroute (relay) nodes.

Run it, then exercise both entry points + the polymorphic typing:

1. Drag-from-pin: drag a wire off any pin and drop it on empty canvas; the
   palette popup should offer "Reroute" (category: utilities). Picking it spawns a
   reroute wired to the dragged pin.
2. Insert on a link: right-click an existing link -> "Insert reroute here". The
   link is split into  src -> reroute -> dst.
3. Adopt-on-connect typing (P1): wire  make_int -> reroute -> need_int  (ok). Now
   try to also feed  make_str -> reroute : it must be REJECTED (the reroute would
   become str and break reroute -> need_int). Disconnect the reroute's input and it
   reverts to accepting anything again.
4. Reroute chains: chain several reroutes between make_int and need_int; the whole
   chain should carry int and stay type-checked.
5. Persistence: save the workspace (Ctrl+S), reopen; the reroutes and their wiring
   should come back, re-typed from the connections.
"""
import fiatlight as fl


@fl.with_fiat_attributes(fiat_tags=["math"])
def make_int() -> int:
    return 21


@fl.with_fiat_attributes(fiat_tags=["text"])
def make_str() -> str:
    return "hello"


@fl.with_fiat_attributes(fiat_tags=["math"])
def need_int(x: int) -> int:
    return x * 2


fl.run_graph_composer([make_int, make_str, need_int], app_name="usability_reroute")
