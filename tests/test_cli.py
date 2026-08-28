import json

from click.testing import CliRunner

from seigaiha.cli import cli
from tests.conftest import normalise_svg

# `cli` is wrapped in `@logger.catch`, which hides the click command from the
# test runner; the command itself is kept on `__wrapped__`.
command = getattr(cli, "__wrapped__", cli)


def run(arguments):
    result = CliRunner().invoke(command, arguments, catch_exceptions=False)
    assert result.exit_code == 0, result.output

    return result


def test_single_element_writes_svg_and_png(tmp_path, preset_file, single_preset):
    preset = preset_file(single_preset)
    output = tmp_path / "output"
    output.mkdir()

    run(["-i", str(preset), "-o", str(output), "--no-unique-filename"])

    assert sorted(path.name for path in output.iterdir()) == [
        "preset.png",
        "preset.svg",
    ]
    assert (output / "preset.png").read_bytes()[:8] == b"\x89PNG\r\n\x1a\n"


def test_single_element_svg(tmp_path, preset_file, single_preset, snapshot):
    preset = preset_file(single_preset)
    output = tmp_path / "output"
    output.mkdir()

    run(["-i", str(preset), "-o", str(output), "-e", '["svg"]', "--no-unique-filename"])

    assert normalise_svg((output / "preset.svg").read_text()) == snapshot


def test_pattern_writes_an_extra_file_per_extension(
    tmp_path, preset_file, pattern_preset
):
    preset = preset_file(pattern_preset)
    output = tmp_path / "output"
    output.mkdir()

    run(["-i", str(preset), "-o", str(output), "--no-unique-filename"])

    assert sorted(path.name for path in output.iterdir()) == [
        "preset.png",
        "preset.svg",
        "preset_seigaiha.png",
        "preset_seigaiha.svg",
    ]


def test_pattern_svg(tmp_path, preset_file, pattern_preset, snapshot):
    preset = preset_file(pattern_preset)
    output = tmp_path / "output"
    output.mkdir()

    run(["-i", str(preset), "-o", str(output), "-e", '["svg"]', "--no-unique-filename"])

    assert normalise_svg((output / "preset_seigaiha.svg").read_text()) == snapshot


def test_broken_pattern_svg(tmp_path, preset_file, broken_pattern_preset, snapshot):
    preset = preset_file(broken_pattern_preset)
    output = tmp_path / "output"
    output.mkdir()

    run(["-i", str(preset), "-o", str(output), "-e", '["svg"]', "--no-unique-filename"])

    assert normalise_svg((output / "preset_seigaiha.svg").read_text()) == snapshot


def test_broken_pattern_uses_the_broken_colours(
    tmp_path, preset_file, pattern_preset, broken_pattern_preset
):
    # The second broken colour, 200/191/231, is not part of the base palette.
    broken_colour = "#c8bfe7"
    output = tmp_path / "output"
    output.mkdir()

    for name, preset in (("plain", pattern_preset), ("broken", broken_pattern_preset)):
        run(
            [
                "-i",
                str(preset_file(preset, f"{name}.json")),
                "-o",
                str(output),
                "-e",
                '["svg"]',
                "--no-unique-filename",
            ]
        )

    assert broken_colour not in (output / "plain_seigaiha.svg").read_text()
    assert broken_colour in (output / "broken_seigaiha.svg").read_text()


def test_render_differs_per_seed(tmp_path, preset_file, broken_pattern_preset):
    output = tmp_path / "output"
    output.mkdir()

    for name, seed in (("first", 42), ("second", 7)):
        run(
            [
                "-i",
                str(
                    preset_file({**broken_pattern_preset, "seed": seed}, f"{name}.json")
                ),
                "-o",
                str(output),
                "-e",
                '["svg"]',
                "--no-unique-filename",
            ]
        )

    assert (output / "first_seigaiha.svg").read_text() != (
        output / "second_seigaiha.svg"
    ).read_text()


def test_render_is_reproducible_for_a_seeded_preset(
    tmp_path, preset_file, broken_pattern_preset
):
    preset = preset_file(broken_pattern_preset)
    first = tmp_path / "first"
    second = tmp_path / "second"
    for output in (first, second):
        output.mkdir()
        run(
            [
                "-i",
                str(preset),
                "-o",
                str(output),
                "-e",
                '["svg"]',
                "--no-unique-filename",
            ]
        )

    assert normalise_svg((first / "preset_seigaiha.svg").read_text()) == normalise_svg(
        (second / "preset_seigaiha.svg").read_text()
    )


def test_unique_filenames_carry_a_datetime_suffix(tmp_path, preset_file, single_preset):
    preset = preset_file(single_preset)
    output = tmp_path / "output"
    output.mkdir()

    run(["-i", str(preset), "-o", str(output), "-e", '["svg"]'])

    written = list(output.iterdir())
    assert len(written) == 1
    assert normalise_svg(written[0].name) == "preset_<datetime>.svg"


def test_directory_input_renders_every_preset(tmp_path, single_preset, pattern_preset):
    presets = tmp_path / "presets"
    presets.mkdir()
    (presets / "single.json").write_text(json.dumps(single_preset))
    (presets / "pattern.json").write_text(json.dumps(pattern_preset))
    output = tmp_path / "output"
    output.mkdir()

    run(
        ["-i", str(presets), "-o", str(output), "-e", '["svg"]', "--no-unique-filename"]
    )

    assert sorted(path.name for path in output.iterdir()) == [
        "pattern.svg",
        "pattern_seigaiha.svg",
        "single.svg",
    ]


def test_output_file_path_is_respected(tmp_path, preset_file, single_preset):
    preset = preset_file(single_preset)
    target = tmp_path / "custom.svg"

    run(["-i", str(preset), "-o", str(target), "-e", '["svg"]', "--no-unique-filename"])

    assert target.is_file()


def test_preset_defaults_are_applied(tmp_path, preset_file, colours):
    preset = preset_file({"fractions": 3, "colours": colours})
    output = tmp_path / "output"
    output.mkdir()

    run(["-i", str(preset), "-o", str(output), "-e", '["svg"]', "--no-unique-filename"])

    # Falls back to the default resolution of 2500 and 36 edges.
    content = (output / "preset.svg").read_text()
    assert 'width="2500.0px" height="2500.0px"' in content
