import ast
from pathlib import Path

import click

from seigaiha.helper import read_json, files_in_dir


class InputPathChecker:
    def __call__(self, ctx, param, value):
        if value is None:
            raise click.BadParameter("No path provided")

        results = []
        for batch_number, path in enumerate(value):
            current_batch = {"batch": batch_number + 1}
            p = Path(path)
            if p.exists():
                if p.is_file():
                    current_batch = {
                        **current_batch,
                        "input": {
                            "given": path,
                            "resolved": [{"path": p, "content": read_json(p)}],
                        },
                    }
                elif p.is_dir():
                    files = files_in_dir(p)
                    amount_of_files_in_directory = len(files)
                    if amount_of_files_in_directory == 0:
                        raise click.BadParameter("No files found in directory")

                    for current_file_index, current_file_path in enumerate(files):
                        files[current_file_index] = {
                            "path": current_file_path,
                            "content": read_json(current_file_path),
                        }

                    current_batch = {
                        **current_batch,
                        "input": {"given": path, "resolved": files},
                    }
                else:
                    raise click.BadParameter("Not a file or directory")
            else:
                raise click.BadParameter("Path does not exist")
            results.append(current_batch)

        return results


class OutputPathChecker:
    def __call__(self, ctx, param, value):
        if value is None:
            raise click.BadParameter("No path provided")

        amount_of_current_param_values = len(value)
        input_path = ctx.params.get("input_path")
        if input_path is None:
            input_path_checker = InputPathChecker()
            input_path = input_path_checker(ctx, param, ["./input"])

        amount_of_input_values = len(input_path)

        if (
            amount_of_input_values != amount_of_current_param_values
            and amount_of_current_param_values != 1
        ):
            raise click.BadParameter(
                f"The amount of input values ({amount_of_input_values}) does not "
                f"equal amount of output values ({amount_of_current_param_values})."
            )

        to_be_enumerated = value
        if amount_of_input_values != amount_of_current_param_values:
            to_be_enumerated = value * amount_of_input_values

        results = []
        for batch_number, path in enumerate(to_be_enumerated):
            current_batch = {"batch": batch_number + 1}
            p = Path(path)
            if p.suffix:
                if not p.parent.is_dir():
                    raise FileNotFoundError(
                        f"The parent directory `{str(p.parent)}` "
                        f"for output argument `{str(p)}` does not exist."
                    )
                else:
                    current_batch = {
                        **current_batch,
                        "output": {"given": path, "resolved": p},
                    }
            else:
                if not p.is_dir():
                    p.mkdir()
                current_batch = {
                    **current_batch,
                    "output": {"given": path, "resolved": p},
                }
            results.append(current_batch)

        return results


class OptionalValueChecker:
    def __call__(self, ctx, param, value: tuple):
        if value is None:
            raise click.BadParameter("No path provided")

        amount_of_current_param_values = len(value)
        input_path = ctx.params.get("input_path")
        if input_path is None:
            input_path_checker = InputPathChecker()
            input_path = input_path_checker(ctx, param, ["./input"])

        amount_of_input_values = len(input_path)

        to_be_enumerated = value
        if amount_of_input_values != amount_of_current_param_values:
            to_be_enumerated = value * amount_of_input_values

        results = []
        for batch_number, val in enumerate(to_be_enumerated):
            try:
                val = ast.literal_eval(val)
            except ValueError:
                raise click.BadParameter(str(val))

            current_batch: dict = {"batch": batch_number + 1, param.name: val}

            results.append(current_batch)

        return results
