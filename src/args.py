# -*- coding: utf-8 -*-

import argparse
from pathlib import Path
from rich.traceback import install
from src.general import is_json

install()


def files_in_directory(file_path, file_types=None):
    """
    Get the files in the specified directory.

    Parameters
    ----------
    file_path : str
        Path of input directory.
    file_types : list, optional
        Allowed extension to look for. The default is ['*.json'].

    Returns
    -------
    list
        List of Path objects in specified directory.

    """

    if file_types is None:
        file_types = ["*.json"]

    return [f for f_ in [Path(file_path).rglob(e) for e in file_types] for f in f_]


class InputCheck(argparse.Action):
    """
    Checks if the specified input file or directory exists.
    If constant is set to false, directories that do not exist will be created.
    """

    def __call__(self, parser, args, values, option_string=None):
        """
        File/Directory argument checks

        Parameters
        ----------
        parser
            Argument parser.
        args
            Arguments.
        values
            Argument values.
        option_string
            Descriptional string. The default is None.

        Raises
        ------
        FileNotFoundError
            The specified File or Directory could not resolved.

        Returns
        -------
        None

        """

        all_values = []
        for fl in values:
            p = Path(f"preset/{fl}").resolve()
            if not self.const:
                if p.suffix:
                    if is_json(fl):
                        all_values.append({"type": "json", "value": fl})
                    else:
                        all_values.append({"type": "file", "value": p})
                else:
                    if is_json(fl):
                        all_values.append({"type": "json", "value": fl})
            else:
                if is_json(fl):
                    all_values.append({"type": "json", "value": fl})
                if not p.exists():
                    raise FileNotFoundError(
                        f"The specified path `{fl}` does not exist."
                    )
                if p.is_file():
                    all_values.append({"type": "file", "value": p})

        setattr(args, self.dest, all_values)
