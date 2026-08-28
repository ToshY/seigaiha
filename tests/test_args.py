import json

import click
import pytest

from seigaiha.args import InputPathChecker, OptionalValueChecker, OutputPathChecker


@pytest.fixture
def context():
    """
    Bare click context; callbacks read `input_path` from `ctx.params`.
    """

    return click.Context(click.Command("cli"))


@pytest.fixture
def input_batches(context, tmp_path, single_preset):
    """
    Resolved input for a single batch, as `InputPathChecker` would return it.
    """

    path = tmp_path / "preset.json"
    path.write_text(json.dumps(single_preset))
    batches = InputPathChecker()(context, None, [str(path)])
    context.params["input_path"] = batches

    return batches


def test_input_path_checker_resolves_file(context, tmp_path, single_preset):
    path = tmp_path / "preset.json"
    path.write_text(json.dumps(single_preset))

    result = InputPathChecker()(context, None, [str(path)])

    assert len(result) == 1
    assert result[0]["batch"] == 1
    assert result[0]["input"]["given"] == str(path)
    assert result[0]["input"]["resolved"] == [{"path": path, "content": single_preset}]


def test_input_path_checker_resolves_directory(context, tmp_path, single_preset):
    for name in ("a.json", "b.json"):
        (tmp_path / name).write_text(json.dumps(single_preset))

    result = InputPathChecker()(context, None, [str(tmp_path)])

    resolved = result[0]["input"]["resolved"]
    assert sorted(item["path"].name for item in resolved) == ["a.json", "b.json"]
    assert all(item["content"] == single_preset for item in resolved)


def test_input_path_checker_numbers_batches(context, tmp_path, single_preset):
    first = tmp_path / "first.json"
    second = tmp_path / "second.json"
    for path in (first, second):
        path.write_text(json.dumps(single_preset))

    result = InputPathChecker()(context, None, [str(first), str(second)])

    assert [item["batch"] for item in result] == [1, 2]


def test_input_path_checker_rejects_empty_directory(context, tmp_path):
    with pytest.raises(click.BadParameter, match="No files found in directory"):
        InputPathChecker()(context, None, [str(tmp_path)])


def test_input_path_checker_rejects_missing_path(context, tmp_path):
    with pytest.raises(click.BadParameter, match="Path does not exist"):
        InputPathChecker()(context, None, [str(tmp_path / "nope.json")])


def test_input_path_checker_rejects_none(context):
    with pytest.raises(click.BadParameter, match="No path provided"):
        InputPathChecker()(context, None, None)


def test_output_path_checker_accepts_existing_directory(
    context, tmp_path, input_batches
):
    result = OutputPathChecker()(context, None, [str(tmp_path)])

    assert result == [
        {"batch": 1, "output": {"given": str(tmp_path), "resolved": tmp_path}}
    ]


def test_output_path_checker_creates_missing_directory(
    context, tmp_path, input_batches
):
    target = tmp_path / "output"

    OutputPathChecker()(context, None, [str(target)])

    assert target.is_dir()


def test_output_path_checker_accepts_file_path(context, tmp_path, input_batches):
    target = tmp_path / "pattern.svg"

    result = OutputPathChecker()(context, None, [str(target)])

    assert result[0]["output"]["resolved"] == target


def test_output_path_checker_rejects_file_with_missing_parent(
    context, tmp_path, input_batches
):
    target = tmp_path / "missing" / "pattern.svg"

    with pytest.raises(FileNotFoundError, match="does not exist"):
        OutputPathChecker()(context, None, [str(target)])


def test_output_path_checker_broadcasts_single_value(context, tmp_path, single_preset):
    first = tmp_path / "first.json"
    second = tmp_path / "second.json"
    for path in (first, second):
        path.write_text(json.dumps(single_preset))
    context.params["input_path"] = InputPathChecker()(
        context, None, [str(first), str(second)]
    )

    result = OutputPathChecker()(context, None, [str(tmp_path)])

    assert [item["batch"] for item in result] == [1, 2]


def test_output_path_checker_rejects_count_mismatch(context, tmp_path, single_preset):
    first = tmp_path / "first.json"
    second = tmp_path / "second.json"
    for path in (first, second):
        path.write_text(json.dumps(single_preset))
    context.params["input_path"] = InputPathChecker()(
        context, None, [str(first), str(second)]
    )
    outputs = [str(tmp_path / "a"), str(tmp_path / "b"), str(tmp_path / "c")]

    with pytest.raises(click.BadParameter, match="does not equal amount of output"):
        OutputPathChecker()(context, None, outputs)


def test_output_path_checker_rejects_none(context, input_batches):
    with pytest.raises(click.BadParameter, match="No path provided"):
        OutputPathChecker()(context, None, None)


def test_optional_value_checker_parses_literal(context, input_batches):
    parameter = click.Option(["--extension", "-e"])

    result = OptionalValueChecker()(context, parameter, ('["svg", "png"]',))

    assert result == [{"batch": 1, "extension": ["svg", "png"]}]


def test_optional_value_checker_broadcasts_single_value(
    context, tmp_path, single_preset
):
    first = tmp_path / "first.json"
    second = tmp_path / "second.json"
    for path in (first, second):
        path.write_text(json.dumps(single_preset))
    context.params["input_path"] = InputPathChecker()(
        context, None, [str(first), str(second)]
    )
    parameter = click.Option(["--extension", "-e"])

    result = OptionalValueChecker()(context, parameter, ('["svg"]',))

    assert result == [
        {"batch": 1, "extension": ["svg"]},
        {"batch": 2, "extension": ["svg"]},
    ]


def test_optional_value_checker_rejects_invalid_literal(context, input_batches):
    parameter = click.Option(["--extension", "-e"])

    with pytest.raises(click.BadParameter):
        OptionalValueChecker()(context, parameter, ("not-a-literal",))


def test_optional_value_checker_rejects_none(context, input_batches):
    parameter = click.Option(["--extension", "-e"])

    with pytest.raises(click.BadParameter, match="No path provided"):
        OptionalValueChecker()(context, parameter, None)
