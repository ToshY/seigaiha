"""Arguments"""

import argparse
from pathlib import Path
from rich.traceback import install
from src.general import is_json

install()


def files_in_directory(file_path, file_types=None):
    """
    Get the files in the specified directory.
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
        """

        all_values = []
        for preset_file_value in values:
            preset_file_path = Path(f"preset/{preset_file_value}").resolve()
            if not self.const:
                if preset_file_path.suffix:
                    if is_json(preset_file_value):
                        all_values.append({"type": "json", "value": preset_file_value})
                    else:
                        all_values.append({"type": "file", "value": preset_file_path})
                else:
                    if is_json(preset_file_value):
                        all_values.append({"type": "json", "value": preset_file_value})
            else:
                if is_json(preset_file_value):
                    all_values.append({"type": "json", "value": preset_file_value})
                if not preset_file_path.exists():
                    raise FileNotFoundError(
                        f"The specified path `{preset_file_value}` does not exist."
                    )
                if preset_file_path.is_file():
                    all_values.append({"type": "file", "value": preset_file_path})

        setattr(args, self.dest, all_values)
