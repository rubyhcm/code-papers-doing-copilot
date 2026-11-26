from .bgl import BGL_Dataset

def load_dataset(data_path, encoder_path, device="cpu", batch_size=64):
    """Loads the dataset."""

    dataset = BGL_Dataset(
        root=data_path,
        encoder_path=encoder_path,
        device=device,
        batch_size=batch_size,
    )

    return dataset
