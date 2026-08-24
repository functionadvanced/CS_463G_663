import torch

from hw5_starter import build_loaders, set_seed, two_digit_label


def main():
    set_seed(42)
    train_loader, test_loader = build_loaders(batch_size=16)
    images, labels = next(iter(train_loader))

    assert len(train_loader.dataset) == 30_000
    assert len(test_loader.dataset) == 5_000
    assert images.shape == (16, 1, 28, 56)
    assert labels.dtype == torch.int64
    assert 0 <= int(labels.min()) <= int(labels.max()) <= 99
    assert two_digit_label(3) == "03"
    assert two_digit_label(30) == "30"
    print("Homework 5 data setup passed.")


if __name__ == "__main__":
    main()
