# -*- coding: utf-8 -*-
"""
Created on Thu Dec  12 20:52:08 2020

@author: ToshY
"""

import collections
import functools
import json


def read_file(input_file: str, split_lines: bool = True, custom_encoding: str = "latin-1"):
    """
    Read in file

    Parameters
    ----------
    input_file : str
        Input file name.
    split_lines : bool, optional
        Split lines. The default is True.
    custom_encoding : str
        The encoding to use for the file. The default is latin-1.

    Returns
    -------
    list
        Dictionary with the content and encoding.
    """

    input_file_read = open(str(input_file), mode="r", encoding=custom_encoding).read()

    if split_lines:
        return {"content": input_file_read.splitlines(), "encoding": custom_encoding}

    return {"content": input_file_read, "encoding": custom_encoding}


def read_json(input_file: str) -> dict:
    """
    Read in JSON file.

    Parameters
    ----------
    input_file : str
        The specified input JSON file.

    Returns
    -------
    data : dictionary
        The data in JSON format.
    """

    with open(input_file) as json_file:
        data = json.load(json_file)

    return data


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

    return [(k, v) for k, v in key_value_dict.items()]


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
        List of dictionaries splitted by key.
    """

    result = collections.defaultdict(list)
    keys = []
    for d in list_of_dicts:
        result[d[key]].append(d)
        if d[key] not in keys:
            keys.append(d[key])

    return list(result.values()), keys
