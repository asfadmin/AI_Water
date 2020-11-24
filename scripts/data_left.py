import os
from argparse import ArgumentParser


def get_paths(dataset: str):
    dataset_path = os.path.join("datasets", dataset)
    dataset_path_groomed = f"{dataset_path}_Groomed"
    return {
        "original": {
            "test_path": os.path.join(dataset_path, "test"),
            "train_path": os.path.join(dataset_path, "train")
        },
        "groomed": {
            "test_path": os.path.join(dataset_path_groomed, "test"),
            "train_path": os.path.join(dataset_path_groomed, "train")
        }
    }


def get_path_stats(individual_paths: str, key: str):
    count = 0
    for path in individual_paths:
        for file in os.listdir(individual_paths[path]):
            if not file.endswith(".tiff"):
                continue
            count += 1

    return {
        key: int(count)/3
    }


def get_stats(dataset: str):
    paths = get_paths(dataset)
    stats = []
    for key in paths:
        stats.append(get_path_stats(paths[key], key))

    return {
        "original": stats[0]['original'],
        "groomed": stats[1]['groomed'],
        "total": stats[0]['original'] + stats[1]['groomed']
    }


def from_terminal(dataset: str):
    stats = get_stats(dataset)
    print(f"You've done {stats['groomed']} out of {stats['total']}")


if __name__ == "__main__":
    p = ArgumentParser()

    p.add_argument("dataset", help="name of dataset")
    p.set_defaults(func=from_terminal)

    args = p.parse_args()
    if hasattr(args, 'func'):
        args.func(args.dataset)
    else:
        p.print_help()