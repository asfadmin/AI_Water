import os

from ..config import DATASETS_DIR


def dataset_dir(dataset: str) -> str:
    return os.path.join(DATASETS_DIR, dataset)
