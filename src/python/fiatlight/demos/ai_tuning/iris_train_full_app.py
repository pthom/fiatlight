# A complete application which provides a function graph with several nodes where the user can:
# - train a model on the Iris dataset
# - save and reload the trained model (we use `add_gui_node` to add "GUI only" nodes for these actions)
# - edit the parameters for splitting the dataset, and edit the hyperparameters for training the model
#   (those parameters are saved and reloaded upon restarting the application)
# - plot the decision boundary of the trained model

# type: ignore
"""Irises classification with a simple MLP model
================================================
We train a simple MLP model to classify the Iris dataset. The model has one hidden layer with ReLU activation.

What FiatLight brings to this example
-------------------------------------
- A few hyperparameters can be tuned via the GUI: the number of epochs, the learning rate, and the weight decay, etc.
- During the training process several, a figure shows the accuracy and loss curves, for both training and test sets.
- The training can be stopped at any time by clicking on the "Stop" button in the GUI.

How this was done
-----------------
- We created two Pydantic models, `SplitParams` and `HyperParams` to define the parameters
  for splitting the dataset and training the model.
  Since these models are decorated with `@fl.base_model_with_gui_registration()`,
  a GUI is automatically generated for them.
- We defined a `IrisDataset` which contains the training and test sets as PyTorch tensors.
- We defined a `SimpleMLP` class to create a simple MLP model with one hidden layer.
- We defined a `GlobalState` class to store the global state of this whole module.

"""
import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.decomposition import PCA
import numpy as np
from pydantic import BaseModel
import fiatlight as fl
import logging
import matplotlib; matplotlib.use("Agg")  # this is needed to render the plots in the GUI # noqa
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from imgui_bundle import imgui


# SplitParams: parameters for loading and splitting the dataset
# This model will be used to define the parameters for splitting the dataset
# It is presented in the GUI for the user to set the parameters
# (which is why it is decorated with @fl.base_model_with_gui_registration())
# We are using a Pydantic BaseModel here, because it enables to save/reload the parameters
# upon restarting the application
@fl.base_model_with_gui_registration(
    test_size__tooltip="Fraction of the dataset to include in the test split",
    test_size__range=(0.0, 1),
    random_state__tooltip="Random seed for splitting the dataset",
)
class SplitParams(BaseModel):
    """Parameters for loading and splitting the dataset"""

    test_size: float = 0.3
    random_state: int = 42


@fl.base_model_with_gui_registration(
    num_epochs__range=(1, 1000),
    num_epochs__tooltip="Number of epochs for training",
    hidden_size__range=(1, 100),
    hidden_size__tooltip="Size of the hidden layer",
    learning_rate__range=(0.00001, 1),
    learning_rate__tooltip="Learning rate for training",
    update_plots_every__range=(1, 100),
    update_plots_every__tooltip="Update plots every n epochs (0 to disable)",
)
class HyperParams(BaseModel):
    """Hyperparameters for training the model"""

    num_epochs: int = 100
    hidden_size: int = 10
    learning_rate: float = 0.01
    update_plots_every: int = 10  # setting update_plots_every this to a low value may slow down the training


class IrisDataset:
    """Iris dataset with training and test sets as PyTorch tensors"""

    X_train: torch.Tensor
    X_test: torch.Tensor
    y_train: torch.Tensor
    y_test: torch.Tensor

    def __init__(self, dataset_params: SplitParams):
        # Load the Iris dataset
        iris = load_iris()
        X = iris.data  # Features
        y = iris.target  # Labels

        # Split into training and test sets (numpy arrays)
        X_train_np, X_test_np, y_train_np, y_test_np = train_test_split(
            X, y, test_size=dataset_params.test_size, random_state=dataset_params.random_state
        )

        # Convert to tensors
        self.X_train = torch.tensor(X_train_np, dtype=torch.float32)
        self.y_train = torch.tensor(y_train_np, dtype=torch.long)
        self.X_test = torch.tensor(X_test_np, dtype=torch.float32)
        self.y_test = torch.tensor(y_test_np, dtype=torch.long)


class SimpleMLP(nn.Module):
    """Simple MLP model with one hidden layer.
    This is the model which we will train on the Iris dataset.
    """

    def __init__(self, input_size, hidden_size, num_classes):
        super(SimpleMLP, self).__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(hidden_size, num_classes)

    def forward(self, x):
        out = self.fc1(x)
        out = self.relu(out)
        out = self.fc2(out)
        return out


class GlobalState:
    """Global state for this module"""

    split_params: SplitParams
    hyper_params: HyperParams

    iris_dataset: IrisDataset
    model: SimpleMLP | None = None


GLOBALS = GlobalState()


def gui_edit_split_params(
    split_params: SplitParams = SplitParams(),
) -> None:
    """Edit the split parameters"""
    # This function is presented in the function graph, so that the user can edit the split parameters
    # It does nothing apart from setting the split_params in the global state:
    # here we take advantage of the fact that Fiatlight will
    #   - automatically generate a GUI for the SplitParams model
    #   - automatically save and reload the parameters upon restarting the application
    GLOBALS.split_params = split_params
    GLOBALS.iris_dataset = IrisDataset(split_params)


def gui_edit_hyperparams(
    hyper_params: HyperParams = HyperParams(),
) -> None:
    """Edit the hyperparameters"""
    # Same as above, but for the hyperparameters
    GLOBALS.hyper_params = hyper_params


#
# We enclose the training code in a function so that this function can be called by FiatLight
#
@fl.with_fiat_attributes(
    invoke_async_stoppable=True,
    invoke_manually=True,
    invoke_always_dirty=True,
)
@fl.with_fiat_attributes(invoke_async=True, invoke_manually=True)
def gui_perform_training() -> None:
    """A function to train the model on the Iris dataset. It will be presented in the GUI."""
    global GLOBALS

    # Model initialization
    input_size = GLOBALS.iris_dataset.X_train.shape[1]
    num_classes = 3
    GLOBALS.model = SimpleMLP(input_size, GLOBALS.hyper_params.hidden_size, num_classes)

    # Loss and optimizer
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(GLOBALS.model.parameters(), lr=GLOBALS.hyper_params.learning_rate)

    # Lists to store loss and accuracy (for plotting)
    train_loss_list = []
    train_acc_list = []
    test_loss_list = []
    test_acc_list = []

    # Training loop
    for epoch in range(GLOBALS.hyper_params.num_epochs):
        # Check if the user wants to stop the training
        if hasattr(gui_perform_training, "invoke_async_shall_stop") and gui_perform_training.invoke_async_shall_stop:
            gui_perform_training.invoke_async_shall_stop = False  # reset the flag
            break

        GLOBALS.model.train()

        # Forward pass
        outputs = GLOBALS.model(GLOBALS.iris_dataset.X_train)
        loss = criterion(outputs, GLOBALS.iris_dataset.y_train)
        train_loss_list.append(loss.item())

        # Backward and optimize
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        # Compute accuracy
        _, predicted = torch.max(outputs, 1)
        correct = (predicted == GLOBALS.iris_dataset.y_train).sum().item()
        accuracy = correct / GLOBALS.iris_dataset.y_train.size(0)
        train_acc_list.append(accuracy)

        # Compute loss and accuracy on the test set
        GLOBALS.model.eval()
        with torch.no_grad():
            outputs_test = GLOBALS.model(GLOBALS.iris_dataset.X_test)
            loss_test = criterion(outputs_test, GLOBALS.iris_dataset.y_test)
            test_loss_list.append(loss_test.item())
            _, predicted_test = torch.max(outputs_test, 1)
            correct_test = (predicted_test == GLOBALS.iris_dataset.y_test).sum().item()
            test_accuracy = correct_test / GLOBALS.iris_dataset.y_test.size(0)
            test_acc_list.append(test_accuracy)

        # Logging loss and accuracy
        logging.warning(
            f"""Epoch [{epoch+1}/{GLOBALS.hyper_params.num_epochs}],
                Train Loss: {loss.item():.4f}, Accuracy: {accuracy:.4f}
                Test Loss: {loss_test.item():.4f}, Test Accuracy: {test_accuracy:.4f}"""
        )

        # Update loss/accuracy plots in real-time
        shall_update_plots = (
            GLOBALS.hyper_params.update_plots_every > 0 and epoch % GLOBALS.hyper_params.update_plots_every == 0
        )
        shall_update_plots |= GLOBALS.hyper_params.num_epochs - 1
        if shall_update_plots:
            fig = plt.figure(figsize=(7, 3))

            plt.subplot(1, 2, 1)
            plt.plot(train_loss_list, label="Train Loss")
            plt.plot(test_loss_list, label="Test Loss")
            plt.xlabel("Epoch")
            plt.ylabel("Loss")
            plt.legend()
            plt.title("Loss vs. Epochs")

            plt.subplot(1, 2, 2)
            plt.plot(train_acc_list, label="Train Accuracy")
            plt.plot(test_acc_list, label="Test Accuracy")
            plt.xlabel("Epoch")
            plt.ylabel("Accuracy")
            plt.legend()
            plt.title("Accuracy vs. Epochs")

            plt.tight_layout()

            # plt.show()
            # We simply replace the call to plt.show() with fiat_tuning:
            fl.add_fiat_attributes(gui_perform_training, fiat_tuning={"epoch": epoch, "draw_accuracy_loss_fig": fig})

    # Optionally, evaluate on the test set
    GLOBALS.model.eval()
    with torch.no_grad():
        outputs_test = GLOBALS.model(GLOBALS.iris_dataset.X_test)
        _, predicted_test = torch.max(outputs_test, 1)
        correct_test = (predicted_test == GLOBALS.iris_dataset.y_test).sum().item()
        test_accuracy = correct_test / GLOBALS.iris_dataset.y_test.size(0)
        logging.warning(f"Test Accuracy: {test_accuracy:.4f}")


@fl.with_fiat_attributes(
    invoke_manually=True,
    invoke_always_dirty=True,
)
def plot_decision_boundary() -> Figure:
    """Plot the decision boundary of the trained model.
    Call this function to visualize the decision boundary of the trained model,
    only after training the model."""

    def do_plot_one_decision_boundary(ax, x, y):
        # Reduce dimensionality for visualization
        pca = PCA(n_components=2)
        X_pca = pca.fit_transform(x)

        # Create a grid to plot decision boundary
        x_min, x_max = X_pca[:, 0].min() - 1, X_pca[:, 0].max() + 1
        y_min, y_max = X_pca[:, 1].min() - 1, X_pca[:, 1].max() + 1
        xx, yy = np.meshgrid(np.arange(x_min, x_max, 0.01), np.arange(y_min, y_max, 0.01))

        # Make predictions on the grid
        Z = GLOBALS.model(torch.tensor(pca.inverse_transform(np.c_[xx.ravel(), yy.ravel()]), dtype=torch.float32))
        Z = Z.argmax(dim=1).detach().numpy()
        Z = Z.reshape(xx.shape)

        # Plot the decision boundary
        ax.contourf(xx, yy, Z, alpha=0.8)
        ax.scatter(X_pca[:, 0], X_pca[:, 1], c=y, edgecolor="k", marker="o")

    global GLOBALS
    fig = plt.figure(figsize=(7, 3))
    ax = fig.add_subplot(111)
    do_plot_one_decision_boundary(ax, GLOBALS.iris_dataset.X_train, GLOBALS.iris_dataset.y_train)
    return fig


def gui_save_model() -> None:
    if imgui.button("Save model"):
        torch.save(GLOBALS.model.state_dict(), "iris_model.pth")


def gui_load_model() -> None:
    if GLOBALS.model is None:
        imgui.text("No model in memory")
    if imgui.button("Load model"):
        GLOBALS.model.load_state_dict(torch.load("iris_model.pth"))


graph = fl.FunctionsGraph()
graph.add_function(gui_edit_split_params)
graph.add_function(gui_edit_hyperparams)
graph.add_function(gui_perform_training)
graph.add_function(plot_decision_boundary)
graph.add_gui_node(gui_save_model)
graph.add_gui_node(gui_load_model)
graph.add_markdown_node(__doc__)
fl.run(graph)
