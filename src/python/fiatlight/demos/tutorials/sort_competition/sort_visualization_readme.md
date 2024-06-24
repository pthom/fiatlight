An interactive visualization of different sorting algorithms, using Fiatlight
=============================================================================

This is a full tutorial that demonstrates many features of Fiatlight:

Part 1:
-------
- How to run a simple function with a GUI provided by Fiatlight
- How to add fiat_attributes to set the ranges of value for numeric widgets.
- How to set the labels for functions and parameters
- How to add a GUI for a pydantic model. How are pydantic validators handled?
- How to create functions that are invoked on demand (i.e. when a button is clicked)

Part 2:
-------
- How to create a custom renderer for a widget.
- How to specify widget sizes in DPI independent units.
- how to use ImPlot to plot large quantities of data at high frame rates

Part 3:
-------
- How to associate a custom widget class for all instances of a given type

Part 4:
-------
- How to use "fiat_tuning" in order to display a function internal state
  is the GUI
  (In our case, we will be graphically displaying the current status of the ordering)
- How to run functions as synchronously
- How to disable the idling
- How to run a composition of functions

Part 5:
-------
- How to run a custom function graph.
- How to add a "GUI Only" node to the graph (i.e. a node that does not have a corresponding function)
- how to add "Documentation" node to the graph

Part 6:
------
- How to create a standalone app version of the sort visualization
  (that will reuse the GUI provided by Fiatlight)
- How to create the layout of an application:
  - Using standard ImGui layout functions (begin_group, same_line, etc)
  - Using Dockable windows
