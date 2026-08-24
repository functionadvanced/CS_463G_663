import random

import matplotlib.pyplot as plt
import torch
from torch import nn
from torch.utils.data import DataLoader, Dataset
from torchvision.datasets import MNIST


class PairedMNIST(Dataset):
    """Non-overlapping, ordered pairs from one official MNIST split."""

    def __init__(self, root: str, train: bool, download: bool = True):
        source = MNIST(root=root, train=train, download=download)
        images = source.data.float().div(255.0)
        labels = source.targets

        left_images = images[0::2]
        right_images = images[1::2]
        self.images = torch.cat(
            (left_images, right_images), dim=2
        ).unsqueeze(1)
        self.labels = labels[0::2] * 10 + labels[1::2]

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, index):
        return self.images[index], self.labels[index]


def set_seed(seed: int):
    random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False


def build_loaders(root="data", batch_size=128):
    train_data = PairedMNIST(root, train=True, download=True)
    test_data = PairedMNIST(root, train=False, download=True)
    train_loader = DataLoader(
        train_data, batch_size=batch_size, shuffle=True
    )
    test_loader = DataLoader(
        test_data, batch_size=batch_size, shuffle=False
    )
    return train_loader, test_loader


def two_digit_label(value: int):
    return f"{value:02d}"


def show_examples(images, labels, predictions=None, count=4):
    figure, axes = plt.subplots(1, count, figsize=(2.5 * count, 2.4))
    if count == 1:
        axes = [axes]
    for index, axis in enumerate(axes):
        axis.imshow(images[index].squeeze().cpu(), cmap="gray")
        true_label = two_digit_label(int(labels[index]))
        if predictions is None:
            title = f"True: {true_label}"
        else:
            predicted = two_digit_label(int(predictions[index]))
            title = f"Pred: {predicted}\nTrue: {true_label}"
        axis.set_title(title)
        axis.axis("off")
    figure.tight_layout()
    return figure


class TwoDigitCNN(nn.Module):
    def __init__(self):
        super().__init__()
        # TODO: define convolution, activation, pooling, and linear layers.
        self.network = None

    def forward(self, images):
        if self.network is None:
            raise NotImplementedError("Define the CNN architecture")
        return self.network(images)


def train_one_epoch(model, loader, loss_function, optimizer, device):
    """Return mean training loss for one epoch."""
    raise NotImplementedError("Implement one training epoch")


def evaluate(model, loader, loss_function, device):
    """Return mean test loss and test accuracy without updating the model."""
    raise NotImplementedError("Implement evaluation")


def main():
    set_seed(42)
    train_loader, test_loader = build_loaders()
    images, labels = next(iter(train_loader))
    print("train pairs:", len(train_loader.dataset))
    print("test pairs:", len(test_loader.dataset))
    print("batch shape:", tuple(images.shape))
    print("label range:", int(labels.min()), int(labels.max()))
    print("Data setup passed. Complete the CNN and learning TODOs next.")


if __name__ == "__main__":
    main()
