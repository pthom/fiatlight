import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from pydantic import BaseModel
from sklearn.preprocessing import StandardScaler
import numpy as np
import fiatlight as fl
import logging
import matplotlib.pyplot as plt


# DatasetParams: parameters for loading and splitting the dataset
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
class DatasetParams(BaseModel):
    """Parameters for loading and splitting the dataset"""

    test_size: float = 0.3
    random_state: int = 42


@fl.base_model_with_gui_registration(
    num_epochs__tooltip="Number of epochs for training",
    num_epochs__range=(1, 1000),
    hidden_size__tooltip="Size of the hidden layer",
    hidden_size__range=(1, 100),
    learning_rate__tooltip="Learning rate for training",
    learning_rate__range=(0.00001, 1),
    learning_rate__slider_logarithmic=True,
    learning_rate__format="%.8f",
    update_plots_every__tooltip="""Update plots every n epochs (0 to disable).
        Warning: setting this to a low value may slow down the training""",
    update_plots_every__range=(1, 100),
)
class HyperParams(BaseModel):
    """Hyperparameters for training the model"""

    num_epochs: int = 100
    hidden_size: int = 10
    learning_rate: float = 0.01
    update_plots_every: int = 10


# Function to load and split the dataset
def load_and_split_data(params: DatasetParams) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    # Load the Iris dataset
    iris = load_iris()
    X = iris.data  # Features
    y = iris.target  # Labels

    # Split into training and test sets
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=params.test_size, random_state=params.random_state
    )

    return X_train, X_test, y_train, y_test


class SimpleMLP(nn.Module):
    """Simple MLP model with one hidden layer"""

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


#
# We enclose the training code in a function so that this function can be called by FiatLight
#
@fl.with_fiat_attributes(
    invoke_async=True,
    invoke_manually=True,
    invoke_always_dirty=True,
    invoke_async_stoppable=True,
)
@fl.with_fiat_attributes(invoke_async=True, invoke_manually=True)
def perform_training(
    dataset_params: DatasetParams,
    hyper_params: HyperParams,
) -> None:
    # Load and preprocess data
    iris = load_iris()
    X = iris.data
    y = iris.target

    scaler = StandardScaler()
    X = scaler.fit_transform(X)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=dataset_params.test_size, random_state=dataset_params.random_state
    )

    # Convert to tensors
    X_train = torch.tensor(X_train, dtype=torch.float32)
    y_train = torch.tensor(y_train, dtype=torch.long)
    X_test = torch.tensor(X_test, dtype=torch.float32)
    y_test = torch.tensor(y_test, dtype=torch.long)

    # Model initialization
    input_size = X_train.shape[1]
    num_classes = 3
    model = SimpleMLP(input_size, hyper_params.hidden_size, num_classes)

    # Loss and optimizer
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=hyper_params.learning_rate)

    # Training parameters
    train_loss_list = []
    train_acc_list = []

    # Training loop
    for epoch in range(hyper_params.num_epochs):
        # Check if the user wants to stop the training
        if hasattr(perform_training, "invoke_async_shall_stop") and perform_training.invoke_async_shall_stop:
            perform_training.invoke_async_shall_stop = False  # reset the flag
            break

        model.train()

        # Forward pass
        outputs = model(X_train)
        loss = criterion(outputs, y_train)
        train_loss_list.append(loss.item())

        # Backward and optimize
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        # Compute accuracy
        _, predicted = torch.max(outputs, 1)
        correct = (predicted == y_train).sum().item()
        accuracy = correct / y_train.size(0)
        train_acc_list.append(accuracy)

        # Logging loss and accuracy
        logging.warning(
            f"Epoch [{epoch+1}/{hyper_params.num_epochs}], Loss: {loss.item():.4f}, Accuracy: {accuracy:.4f}"
        )

        # Update loss/accuracy plots in real-time
        shall_update_plots = hyper_params.update_plots_every > 0 and epoch % hyper_params.update_plots_every == 0
        shall_update_plots |= hyper_params.num_epochs - 1
        if shall_update_plots:
            fig = plt.figure(figsize=(7, 3))

            plt.subplot(1, 2, 1)
            plt.plot(train_loss_list, label="Train Loss")
            plt.xlabel("Epoch")
            plt.ylabel("Loss")
            plt.title("Loss vs. Epochs")

            plt.subplot(1, 2, 2)
            plt.plot(train_acc_list, label="Train Accuracy")
            plt.xlabel("Epoch")
            plt.ylabel("Accuracy")
            plt.title("Accuracy vs. Epochs")

            plt.tight_layout()

            # plt.show()
            # We simply replace the call to plt.show() with fiat_tuning:
            fl.add_fiat_attributes(perform_training, fiat_tuning={"epoch": epoch, "draw_accuracy_loss_fig": fig})

    # Optionally, evaluate on the test set
    model.eval()
    with torch.no_grad():
        outputs_test = model(X_test)
        _, predicted_test = torch.max(outputs_test, 1)
        correct_test = (predicted_test == y_test).sum().item()
        test_accuracy = correct_test / y_test.size(0)
        logging.warning(f"Test Accuracy: {test_accuracy:.4f}")


fl.run(perform_training)
