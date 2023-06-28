"""General"""
import collections
import functools
import json


def read_file(
    input_file: str, split_lines: bool = True, custom_encoding: str = "latin-1"
):
    """
    Read in file
    """

    input_file_read = open(str(input_file), mode="r", encoding=custom_encoding).read()

    if split_lines:
        return {"content": input_file_read.splitlines(), "encoding": custom_encoding}

    return {"content": input_file_read, "encoding": custom_encoding}


def read_json_from_file(input_file: str) -> dict:
    """
    Read in JSON file.
    """

    with open(input_file) as json_file:
        data = json.load(json_file)

    return data


def read_json_from_string(input_string: str):
    """
    Read JSON from string.
    """
    return json.loads(input_string)


def is_json(input_string: str) -> bool:
    """
    Check if valid JSON.
    """
    try:
        json.loads(input_string)
    except ValueError:
        return False
    return True


def find_in_dict(input_list: list, key: str, value: str):
    """
    Find in current list with dictionaries.

    Parameters
    ----------
    input_list : list
        Input list
    key : str
        Key to use.
    value : str
        Value to find.

    Returns
    -------
    TYPE : int | bool
        Returns the index of found element or False.
    """

    for i, dic in enumerate(input_list):
        if dic[key] == value:
            return i

    return False


def remove_empty_dict_values(input_dict: dict) -> dict:
    """
    Get keys from dictionary where the values are not empty.

    Parameters
    ----------
    input_dict : dict
        The specified input dictionary.

    Returns
    -------
    dict
        The input dictionary without the keys that have no empty values.
    """

    return {k: v for k, v in input_dict.items() if v}


def dict_to_list(key_value_dict: dict) -> list:
    """
    Convert dictionary key/values to 1D key:value list

    Parameters
    ----------
    key_value_dict : dict
        The specified input dictionary.

    Returns
    -------
    key_value_list : list
        List of key:value arguments.
    """

    return list(functools.reduce(lambda x, y: x + y, key_value_dict.items()))


def dict_to_tuple(key_value_dict: dict) -> list:
    """
    Convert dictionary key/values to 2D list of key:value tuples.

    Parameters
    ----------
    key_value_dict : dict
        The specified input dictionary.

    Returns
    -------
    key_value_list : list
        List of key:value arguments.
    """

    return list(key_value_dict.items())


def list_to_dict(key_value_list: list) -> dict:
    """
    Convert 1D list to key:value pairs.

    Parameters
    ----------
    key_value_list : list
        The specified input list.

    Returns
    -------
    key_value_dict : dict
        Dict of key-value pair.
    """

    return dict(zip(key_value_list[::2], key_value_list[1::2]))


def split_list_of_dicts_by_key(list_of_dicts: list, key: str = "codec_type") -> list:
    """
    Split list of dictionaries by specified key.

    Parameters
    ----------
    list_of_dicts : list
        List of dictionaries.
    key : string, optional
        The key to split the list of dictionaries on. The default is 'codec_type'.

    Returns
    -------
    result_list : list
        List of dictionaries split by key.
    """

    result = collections.defaultdict(list)
    keys = []
    for current_dict in list_of_dicts:
        result[current_dict[key]].append(current_dict)
        if current_dict[key] not in keys:
            keys.append(current_dict[key])

    return list(result.values()), keys
