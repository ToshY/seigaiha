import json
import re
from pathlib import Path

import pytest

# Every generated SVG embeds a render timestamp in its `<desc>` tag, and unique
# output filenames carry the same suffix. Both have to be masked before a value
# can be snapshotted.
DATETIME_PATTERN = re.compile(r"\d{2}-\d{2}-\d{4}_\d{2}-\d{2}-\d{2}-\d{6}")

# Shapely/numpy can differ in the last bits of a float between platforms, so any
# number with more precision than we care about is rounded before comparing.
LONG_FLOAT_PATTERN = re.compile(r"-?\d+\.\d{7,}")

PRECISION = 6


def normalise_svg(content: str) -> str:
    """
    Make SVG output stable enough to snapshot.
    """

    content = content.replace("\r\n", "\n")
    content = DATETIME_PATTERN.sub("<datetime>", content)

    return LONG_FLOAT_PATTERN.sub(
        lambda match: f"{float(match.group()):.{PRECISION}f}", content
    )


def round_nested(value, precision: int = PRECISION):
    """
    Recursively round floats in (nested) lists, tuples and dicts.
    """

    if isinstance(value, float):
        return round(value, precision)

    if isinstance(value, (list, tuple)):
        return [round_nested(item, precision) for item in value]

    if isinstance(value, dict):
        return {key: round_nested(item, precision) for key, item in value.items()}

    return value


@pytest.fixture
def colours() -> list:
    return [
        {"R": 65, "G": 124, "B": 192, "A": 1},
        {"R": 255, "G": 255, "B": 255, "A": 1},
    ]


@pytest.fixture
def single_preset(colours) -> dict:
    """
    Minimal single element preset; small resolution keeps PNG rendering fast.
    """

    return {
        "seed": 42,
        "fractions": 5,
        "edges": 6,
        "spacing": 0.3,
        "rotation": 0,
        "colours": colours,
        "output": {
            "resolution": 200,
            "svg": {
                "preserveAspectRatio": "xMinYMin meet",
                "style": {"shape-rendering": "crispEdges"},
            },
        },
    }


@pytest.fixture
def pattern_preset(single_preset) -> dict:
    """
    Preset with a repeating pattern, without broken elements.
    """

    return {
        **single_preset,
        "pattern": {
            "horizontal": {"amount": 3, "spacing": 1},
            "vertical": {"amount": 4, "spacing": 0.25},
            "alternate": 1,
        },
    }


@pytest.fixture
def broken_pattern_preset(pattern_preset) -> dict:
    """
    Preset with a "yabure" (broken) pattern.

    Which elements break is drawn with `random.sample`, seeded from the preset
    `seed`; without it every render would pick a different set and none of the
    snapshots below would hold. The grid is a size larger than `pattern_preset`
    and the factor low enough that fewer elements break than there are
    candidates - at a high factor the sample is clamped to "all of them" and the
    seed stops mattering.
    """

    return {
        **pattern_preset,
        "pattern": {
            **pattern_preset["pattern"],
            "horizontal": {"amount": 4, "spacing": 1},
            "vertical": {"amount": 6, "spacing": 0.25},
            "broken": {
                "factor": 0.2,
                "factor_rounding": "round",
                "fractions": 3,
                "skip_edge": True,
                "colours": [
                    {"R": 0, "G": 0, "B": 0, "A": 1},
                    {"R": 200, "G": 191, "B": 231, "A": 1},
                ],
                "images": [],
            },
        },
    }


@pytest.fixture
def preset_file(tmp_path):
    """
    Write a preset to a temporary JSON file and return its path.
    """

    def _write(preset: dict, name: str = "preset.json") -> Path:
        path = tmp_path / name
        path.write_text(json.dumps(preset))

        return path

    return _write
