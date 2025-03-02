import collections
import fnmatch
import json
from pathlib import Path


def files_in_dir(
    path: Path,
    file_types=["*.json"],
):
    """
    Returns a list of files in the given directory that match the specified file types.

    Parameters:
        path (Path): The path to the directory.
        file_types (List[str], optional): A list of file types to match. Defaults to ["*.json"].

    Returns:
        List[Path]: A list of paths to the files in the directory that match the specified file types.
    """

    file_list = [
        f
        for f in path.rglob("*")
        if any(
            fnmatch.fnmatch(f.name.lower(), pattern.lower()) for pattern in file_types
        )
    ]

    return file_list


def read_json(path: Path) -> dict:
    """
    Reads a JSON file from the given path and returns its contents as a dictionary.

    Parameters:
        path (Path): The path to the JSON file.

    Returns:
        dict: The contents of the JSON file as a dictionary.
    """

    with path.open("r") as file:
        data = json.load(file)

    return data


def combine_arguments_by_batch(*lists):
    """
    Combine arguments from multiple lists into batches based on the 'batch' key in each item.

    Parameters:
        *lists: Variable number of lists containing dictionaries with a 'batch' key.

    Returns:
        list: A list of dictionaries containing combined items grouped by their 'batch' key.
    """

    combined = collections.defaultdict(dict)

    for lst in lists:
        for item in lst:
            batch = item["batch"]
            combined[batch].update(item)

    result = [value for key, value in combined.items()]

    return result
