Tutorial An interactive visualization of different sorting algorithms, using Fiatlight
======================================================================================

This is a full tutorial that demonstrates many features of Fiatlight, going from basic to advanced.
Its viewing is recommended for anyone who wants to learn how to use Fiatlight.
![img.png](img.png)


Demo
----
In this tutorial, we will walk you through the process of creating this interactive application, which allows you to visualize and compare the performance of various sorting algorithms.

This tutorial is an intermediate to advanced tutorial which will teach you the following aspects of Fiatlight:
- How to create a GUI for a dataclass / pydantic model
- How to customize the rendering of a function output
- How to use ImPlot to plot large quantities of data at high frame rates
- How to run functions asynchronously
- How to use "fiat_tuning" to display in real-time a function's internal state
  (even if the function is running in a separate thread)
- How to use Fiatlight GUI in standalone applications


Intro - Ready-to-Use Sort Algorithms
------------------------------------

Before we dive into the content, let's quickly look at the sort algorithms and how the latency is handled.

The  code for this tutorial is located in "fiatlight/demos/tutorials/sort_competition".

* "sort_algorithms.py" " provides  ready to use sort algorithms:  bubble sort, quicksort, et cetera.
* "numbers_list.py" " provides a numbers list class which behaves like an integer array,   but exposes a user settable latency for memory access and memory write.
* "numbers_generator" provides a "NumbersGenerationOptions" class which describes how to generate a list of unordered numbers.
It derives from pydantic's BaseModel : it behaves like a serializable dataclass.
* "make_random_number_list" will generate the numbers that shall be sorted.


Part 1 - Automatic GUI for dataclasses and pydantic models
----------------------------------------------------------
+ Gui for a dataclass

The "gui_dataclass_pydantic" tutorial examples provide a detailed explanation on how to automatically create a GUI for a dataclass or a pydantic model.
Note that pydantic models are preferable since Fiatlight will be able to serialize and deserialize them, and thus save user inputs that use them.

These examples show how to use custom attributes to customize the widgets appearance (label, numeric range, etc.).
Let's see them in action.

It also shows how to use validators to ensure that the user inputs are correct. This is possible for dataclasses, and Pydantic validators are also gracefully handled.

- How to add a GUI for a pydantic model.
- How are pydantic validators handled?
- How to add fiat_attributes to set the ranges of value for numeric widgets.
- How to set the labels for functions and parameters
- Add info / attributes for a function
- How to create functions that are invoked on demand (i.e. when a button is clicked)


Part 2 - Customize the rendering of a function output
-----------------------------------------------------
+ Example / function

- How to create a custom renderer for a widget.
- How to specify widget sizes in DPI independent units.
- how to use ImPlot to plot large quantities of data at high frame rates


Part 3 - Use ImPlot to visualize the sorting algorithms
-------------------------------------------------------


Part 3:
-------
- What is the GUI registry? How to register a new type into Fiatlight
- How does AnyDataWithGui work? What are the available callbacks?
- Qick-look at the architecture of Fiatlight from 10,000 feet
- How to create a custom widget class ?
- Look at fiat_kit_skeleton


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


======================================================================================

- Add info / dataclass gui generation
- Add info / attributes for a function


- What is the GUI registry? How to register a new type into Fiatlight
- How does AnyDataWithGui work? What are the available callbacks?
- Qick-look at the architecture of Fiatlight from 10,000 feet
- How to create a custom widget class ?
- Look at fiat_kit_skeleton
