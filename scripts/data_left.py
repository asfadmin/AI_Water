import os
from argparse import ArgumentParser


def get_paths(dataset):
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


def get_path_stats(individual_paths, key):
    count = 0
    for path in individual_paths:
        for file in os.listdir(individual_paths[path]):
            if not file.endswith(".tiff"):
                continue
            count += 1

    return {
        key: int(count)/3
    }


def get_stats(dataset):
    paths = get_paths(dataset)
    stats = []
    for key in paths:
        stats.append(get_path_stats(paths[key], key))

    return {
        "original": stats[0]['original'],
        "groomed": stats[1]['groomed']
    }


def main(dataset: str):
    stats = get_stats(dataset)
    total = stats['groomed'] + stats['original']
    print(f"You've done {stats['groomed']} out of {total}")


if __name__ == "__main__":
    p = ArgumentParser()

    p.add_argument("dataset", help="name of dataset")
    p.set_defaults(func=main)

    args = p.parse_args()
    if hasattr(args, 'func'):
        args.func(args.dataset)
    else:
        p.print_help()