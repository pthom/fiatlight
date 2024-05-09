Draft GPT.... To be reviewed
# High-Level Overview of the Fiatlight Framework

## Package: fiat_core
This is the foundational package of the fiatlight framework. It focuses on wrapping data and functions with GUI elements to facilitate interaction.

**Classes**

* `AnyDataWithGui`: Wraps any type of data with a GUI. This class manages the data value and its associated callbacks, and it provides methods to serialize/deserialize the data to/from JSON.
* `AnyDataGuiCallbacks`: Stores callback functions for AnyDataWithGui, enhancing interactivity by allowing custom widgets and presentations.
* `FunctionWithGui`: Encapsulates a function, enriching it with a GUI based on inferred input and output types. It handles function invocation and manages internal states like exceptions and execution flags.
* `ParamWithGui` and `OutputWithGui`: These classes link parameters and outputs of functions to their GUI representations.
* `FunctionNode`: Represents a node in a function graph, containing links to other function nodes and managing data flow between them.
* `FunctionNodeLink`: Defines a link between outputs of one function node and inputs of another, facilitating data flow in the function graph.
* `FunctionsGraph`: Represents a graph of interconnected FunctionNode instances, effectively mapping the entire functional structure.

## Package: to_gui
This package contains utility functions and classes that register and manage GUI representations for various data types.

**Classes**
* `PrimitiveWithGui` and `CompositeWithGui`: These are specialized classes for primitive and composite data types, respectively, that inherit from AnyDataWithGui to provide GUI features.

**Functions**
* `free_functions`: Includes functions that add input/output GUI elements to functions and manage type registrations via GUI factories.

## Package: fiat_nodes
Focused on the GUI representations of function nodes and graphs using imgui-node-editor, a popular immediate mode GUI toolkit.

**Classes**

* `FunctionNodeGui`: The GUI representation of a FunctionNode, integrating with imgui-node-editor to facilitate visual node-based editing.
* `FunctionNodeLinkGui`: Represents the GUI aspect of a FunctionNodeLink, providing visual connectivity between nodes.
* `FunctionsGraphGui`: Manages the GUI representation of a FunctionsGraph, organizing nodes and links visually for interaction.

## Package: fiat_runner

Handles the runtime aspects of the fiatlight framework, managing parameters and execution of GUI-enabled function graphs.

**Functions**
`Functions` (marked as free_functions): Includes functions that run single functions, compositions of functions, or entire function graphs with the provided parameters.

**Classes**

* `FiatlightGui`: The main runtime class that presents a GUI for interacting with a function graph. It orchestrates the execution and user interaction.
* `FiatlightGuiParams`: Stores configuration and parameters for the GUI application, such as visibility toggles and other settings.
