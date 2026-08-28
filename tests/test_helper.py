import json

import pytest

from seigaiha.helper import combine_arguments_by_batch, files_in_dir, read_json


def test_files_in_dir_finds_json_recursively(tmp_path):
    (tmp_path / "a.json").write_text("{}")
    (tmp_path / "B.JSON").write_text("{}")
    (tmp_path / "ignored.txt").write_text("nope")
    nested = tmp_path / "nested"
    nested.mkdir()
    (nested / "c.json").write_text("{}")

    found = sorted(path.name for path in files_in_dir(tmp_path))

    assert found == ["B.JSON", "a.json", "c.json"]


def test_files_in_dir_honours_file_types(tmp_path):
    (tmp_path / "a.json").write_text("{}")
    (tmp_path / "b.svg").write_text("<svg></svg>")

    found = sorted(path.name for path in files_in_dir(tmp_path, ["*.svg"]))

    assert found == ["b.svg"]


def test_files_in_dir_returns_empty_list_for_empty_directory(tmp_path):
    assert files_in_dir(tmp_path) == []


def test_read_json_returns_contents(tmp_path, single_preset):
    path = tmp_path / "preset.json"
    path.write_text(json.dumps(single_preset))

    assert read_json(path) == single_preset


def test_read_json_raises_on_invalid_json(tmp_path):
    path = tmp_path / "broken.json"
    path.write_text("{not json")

    with pytest.raises(json.JSONDecodeError):
        read_json(path)


def test_combine_arguments_by_batch_merges_per_batch(snapshot):
    combined = combine_arguments_by_batch(
        [{"batch": 1, "input": "a"}, {"batch": 2, "input": "b"}],
        [{"batch": 1, "output": "x"}, {"batch": 2, "output": "y"}],
        [{"batch": 1, "extension": ["svg"]}, {"batch": 2, "extension": ["png"]}],
    )

    assert combined == snapshot


def test_combine_arguments_by_batch_keeps_last_value_for_duplicate_keys():
    combined = combine_arguments_by_batch(
        [{"batch": 1, "input": "first"}],
        [{"batch": 1, "input": "second"}],
    )

    assert combined == [{"batch": 1, "input": "second"}]


def test_combine_arguments_by_batch_without_arguments():
    assert combine_arguments_by_batch() == []
