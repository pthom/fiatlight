# type: ignore
"""Grokking with a simple model on modular addition in Z/53Z
=========================================================

Context
-------
We train a simple model on the modular addition in Z/53Z, i.e. the addition modulo 53.
At the start, the model learn the training set "by heart", and is unable to generalize to the test set.

After a few epochs, the model starts to generalize, and a PCA of the embeddings shows that the model has learned
a representation of the integers modulo 53 in a circular fashion.

What FiatLight brings to this example
-------------------------------------
- A few hyperparameters can be tuned via the GUI: the number of epochs, the learning rate, and the weight decay.
- During the training process several figures are displayed in the GUI
    - a figure showing the accuracy and loss curves
    -  a PCA of the embeddings is also displayed, showing the evolution of the embeddings during training
       and how the model learns to represent the integers modulo 53 in a circular fashion.
- The training can be stopped at any time by clicking on the "Stop" button in the GUI.
"""

# Preliminaries
# =============
# Imports and set the CUDA device, set the seed

import numpy as np
import matplotlib
import fiatlight as fl

matplotlib.use("Agg")  # for faster plotting
import matplotlib.pyplot as plt
import torch
import random
import torch.nn as nn
import torch.nn.functional as F
from sklearn.decomposition import PCA  # type: ignore
from pydantic import BaseModel
import logging


device = "cuda" if torch.cuda.is_available() else "cpu"
# device = "mps"


def set_seed(seed_value=0):
    random.seed(seed_value)
    np.random.seed(seed_value)
    torch.manual_seed(seed_value)

    if device == "cuda":
        torch.cuda.manual_seed(seed_value)
        torch.cuda.manual_seed_all(seed_value)
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False
    if device == "mps":
        torch.mps.manual_seed(seed_value)


# Building the dataset
# =======================
# Define the dataset : addition in
# (i.e. addition modulo P=53), with a random split into train and test sets.
# Half of the set is used for training, the rest is used for tests.

# Prime number for modular addition
P = 53
SEED = 15

# Create the dataset
set_seed(SEED)
data = []
for i in range(P):
    for j in range(P):
        data.append([i, j, (i + j) % P])
data = np.array(data)

# Split into train and test
TRAIN_FRACTION = 0.5
np.random.shuffle(data)
train_data = data[: int(len(data) * TRAIN_FRACTION)]
test_data = data[int(len(data) * TRAIN_FRACTION) :]

# Convert to tensors and create dataloaders with batch size
BATCH_SIZE = 64
train_data = torch.tensor(train_data, dtype=torch.long, device=device)
test_data = torch.tensor(test_data, dtype=torch.long, device=device)
train_loader = torch.utils.data.DataLoader(train_data, batch_size=BATCH_SIZE, shuffle=True)
test_loader = torch.utils.data.DataLoader(test_data, batch_size=BATCH_SIZE, shuffle=False)


#
# Model definition with pytorch
# =============================
D_EMBED = 128
HIDDEN = 256


# Create the NN model
class EmbeddingConcatFFModel(nn.Module):
    def __init__(self):
        super(EmbeddingConcatFFModel, self).__init__()
        self.embed = nn.Embedding(P, D_EMBED)
        self.linear1 = nn.Linear(2 * D_EMBED, HIDDEN)  # 2 * D_EMBED because we concatenate the two embedded tokens
        self.linear2 = nn.Linear(HIDDEN, P)
        self.init_weights()

    def forward(self, x1, x2):
        x1 = self.embed(x1)
        x2 = self.embed(x2)
        x = torch.cat((x1, x2), dim=1)  # Concatenate the embedding of the two tokens
        x = F.relu(self.linear1(x))
        x = self.linear2(x)
        return x

    # Weight initialization
    def init_weights(self):
        for m in self.modules():
            if isinstance(m, nn.Embedding):
                nn.init.xavier_normal_(m.weight)
            if isinstance(m, nn.Linear):
                nn.init.xavier_normal_(m.weight)
                nn.init.zeros_(m.bias)


# Training the model
# ==================
@fl.base_model_with_gui_registration(
    NB_EPOCHS__range=(100, 10000),
    LEARNING_RATE__range=(0.00001, 0.01),
    LEARNING_RATE__slider_logarithmic=True,
    LEARNING_RATE__format="%.5f",  # Fix this (should be inferred from the range)
    WEIGHT_DECAY__range=(0.5, 3),
    WEIGHT_DECAY__tooltip="In this experiment, the weight decay should be about 1",
)
class LearnParameters(BaseModel):
    NB_EPOCHS: int = 1500
    LEARNING_RATE: float = 0.002  # 0.0003
    # WEIGHT_DECAY:float = 0.01
    WEIGHT_DECAY: float = 1


@fl.with_fiat_attributes(
    invoke_async=True,
    invoke_manually=True,
    invoke_async_stoppable=True,
    invoke_always_dirty=True,
)
def perform_training(learn_parameters: LearnParameters) -> None:
    set_seed(SEED)
    model = EmbeddingConcatFFModel().to(device)

    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.AdamW(
        model.parameters(), lr=learn_parameters.LEARNING_RATE, weight_decay=learn_parameters.WEIGHT_DECAY
    )

    train_loss_history = []
    train_acc_history = []
    test_loss_history = []
    test_acc_history = []

    for epoch in range(learn_parameters.NB_EPOCHS):
        if fl.get_fiat_attribute(perform_training, "invoke_async_shall_stop", False):
            fl.set_fiat_attribute(perform_training, "invoke_async_shall_stop", False)
            break

        # Training phase
        model.train()
        train_loss = 0.0
        train_acc = 0.0
        for batch in train_loader:
            x1, x2, y = batch[:, 0], batch[:, 1], batch[:, 2]
            optimizer.zero_grad()
            output = model(x1, x2)
            loss = criterion(output, y)
            loss.backward()
            optimizer.step()
            train_loss += loss.item()
            train_acc += (output.argmax(dim=1) == y).sum().item()

        train_loss /= len(train_loader)
        train_loss_history.append(train_loss)
        train_acc /= len(train_data)
        train_acc_history.append(train_acc)

        # Testing phase
        model.eval()
        with torch.no_grad():
            test_loss = 0.0
            test_acc = 0.0
            for batch in test_loader:
                x1, x2, y = batch[:, 0], batch[:, 1], batch[:, 2]
                output = model(x1, x2)
                loss = criterion(output, y)
                test_loss += loss.item()
                test_acc += (output.argmax(dim=1) == y).sum().item()

            test_loss /= len(test_loader)
            test_loss_history.append(test_loss)
            test_acc /= len(test_data)
            test_acc_history.append(test_acc)

        logging.warning(
            f"""Epoch [{epoch+1}/{learn_parameters.NB_EPOCHS}],
            Train Loss: {train_loss:.6f}, Train Accuracy: {train_acc:.6f},
            Test Loss:  {test_loss:.6f},  Test Accuracy: {test_acc:.6f}"""
        )

        # Draw graph via fiat_tuning
        from matplotlib.figure import Figure

        #
        # draw_accuracy_loss_fig / draw_pca_fig:
        # -------------------------------------
        # Figures that will be displayed in the tuning interface
        # during the training process.
        def draw_accuracy_loss_fig() -> Figure:
            fig, axs = plt.subplots(1, 2, figsize=(6, 2.5))  # Create 1 row and 2 columns of subplots

            # First subplot for accuracy
            axs[0].plot(range(epoch + 1), train_acc_history, label="Train Accuracy")
            axs[0].plot(range(epoch + 1), test_acc_history, label="Test Accuracy")
            axs[0].set_xlabel("Epoch")
            axs[0].set_ylabel("Accuracy")
            axs[0].legend()
            axs[0].set_xlim(0, epoch)

            # Second subplot for loss
            axs[1].plot(range(epoch + 1), train_loss_history, label="Train Loss")
            axs[1].plot(range(epoch + 1), test_loss_history, label="Test Loss")
            axs[1].set_xlabel("Epoch")
            axs[1].set_ylabel("Log(Loss)")
            axs[1].set_yscale("log")
            axs[1].legend()
            axs[1].set_xlim(0, epoch)

            plt.tight_layout()  # Adjust spacing to prevent overlap
            return fig

        def draw_pca_fig() -> Figure:
            # Extract embeddings
            # model.eval()
            with torch.no_grad():
                embeddings = model.embed(torch.arange(0, P).to(device)).cpu().numpy()

            # PCA
            NB_COMPONENTS = 12
            pca = PCA(n_components=NB_COMPONENTS)
            embeddings_pca = pca.fit_transform(embeddings)

            # Plot
            ny = int(np.floor(np.sqrt(16 / 9 * NB_COMPONENTS // 2)))
            nx = int(np.ceil((NB_COMPONENTS // 2) / ny))

            fig, axs = plt.subplots(nx, ny, figsize=(16 / 9 * 6 * nx / 3, 6 * ny / 3))
            # plt.figure(figsize=(16 / 9 * 6 * nx, 6 * ny))
            for n in range(NB_COMPONENTS // 2):
                plt.subplot(nx, ny, n + 1)
                plt.scatter(embeddings_pca[:, 2 * n + 0], embeddings_pca[:, 2 * n + 1], marker="o")
                plt.xlim(-2, 2)
                plt.ylim(-2, 2)
                plt.gca().set_aspect("equal")

                # Annotate each point on the scatter plot
                for i, (x, y) in enumerate(embeddings_pca[:, (2 * n + 0) : (2 * n + 2)]):
                    plt.text(x, y, str(i), fontsize=6, ha="right", va="bottom")

                plt.xlabel(f"PC {2 * n + 0}")
                plt.ylabel(f"PC {2 * n + 1}")
            plt.tight_layout()
            return fig

        # Display the figures in fiat_tuning
        if epoch % 10 == 0:
            import time

            t0 = time.time()
            accuracy_loss_fig = draw_accuracy_loss_fig()
            pca_fig = draw_pca_fig()
            time_figs = time.time() - t0
            fl.add_fiat_attributes(
                perform_training,
                fiat_tuning={
                    "time_figs": time_figs,
                    "epoch": epoch,
                    "acc_loss": accuracy_loss_fig,
                    "pca": pca_fig,
                },
            )


perform_training.__doc__ = __doc__
fl.run(perform_training)
