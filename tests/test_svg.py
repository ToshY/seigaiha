import base64
import json
import re
from pathlib import Path

import pytest

from seigaiha.exception import InvalidViewBoxError
from seigaiha.svg import SVGmaker
from tests.conftest import normalise_svg, round_nested

EXTERNAL_SVG = (
    '<?xml version="1.0"?>'
    '<svg xmlns="http://www.w3.org/2000/svg" width="60" height="40">'
    '<circle cx="30" cy="20" r="10"/>'
    "</svg>"
)

EXTERNAL_SVG_WITHOUT_DIMENSIONS = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 60 40">'
    '<circle cx="30" cy="20" r="10"/>'
    "</svg>"
)


@pytest.fixture
def svg_maker(single_preset) -> SVGmaker:
    return SVGmaker(single_preset, [200, 200])


@pytest.fixture
def pattern_svg_maker(pattern_preset) -> SVGmaker:
    return SVGmaker(pattern_preset, [200, 200])


def test_view_box_defaults_to_image_dimensions(single_preset):
    assert SVGmaker(single_preset, [200, 100]).view_box == [0, 0, 200, 100]


def test_view_box_is_kept_when_given(single_preset):
    assert SVGmaker(single_preset, [200, 100], [1, 2, 3, 4]).view_box == [1, 2, 3, 4]


def test_view_box_rejects_non_numerical_values(single_preset):
    with pytest.raises(InvalidViewBoxError, match="only contains numerical values"):
        SVGmaker(single_preset, [200, 100], [0, 0, "200", 100])


def test_preset_is_embedded_as_base64(svg_maker, single_preset):
    decoded = base64.b64decode(svg_maker.safe_base_encoded_preset).decode("utf-8")

    assert json.loads(decoded) == single_preset


@pytest.mark.parametrize(
    ("rgb", "expected"),
    [
        ((0, 0, 0), "#000000"),
        ((255, 255, 255), "#ffffff"),
        ((65, 124, 192), "#417cc0"),
        ((300, -20, 128), "#ff0080"),
    ],
)
def test_rgb_to_hexadecimal_notation(svg_maker, rgb, expected):
    assert svg_maker.rgb_to_hexadecimal_notation(*rgb) == expected


def test_join_view_box_list(svg_maker):
    assert svg_maker._join_view_box_list([0, 0, 200, 100]) == "0 0 200 100"


@pytest.mark.parametrize(
    ("rounding", "value", "expected"),
    [
        ("floor", 2.7, 2),
        ("ceil", 2.1, 3),
        ("round", 2.6, 3),
        ("round", 2.4, 2),
        # numpy rounds halves to even, and anything unknown falls back to round.
        ("round", 2.5, 2),
        (None, 2.6, 3),
    ],
)
def test_round_value_honours_rounding_mode(
    broken_pattern_preset, rounding, value, expected
):
    broken_pattern_preset["pattern"]["broken"]["factor_rounding"] = rounding
    svg_maker = SVGmaker(broken_pattern_preset, [200, 200])

    assert svg_maker._round_value(value) == expected


def test_xml_initialise(svg_maker, snapshot):
    assert normalise_svg(svg_maker.xml_initialise()) == snapshot


def test_xml_initialise_uses_preset_svg_options(single_preset):
    single_preset["output"]["svg"] = {
        "preserveAspectRatio": "none",
        "style": {"shape-rendering": "optimizeSpeed"},
    }

    xml = SVGmaker(single_preset, [200, 200]).xml_initialise()

    assert 'preserveAspectRatio="none"' in xml
    assert "shape-rendering: optimizeSpeed;" in xml


def test_xml_initialise_falls_back_to_defaults(colours):
    xml = SVGmaker({"colours": colours}, [200, 200]).xml_initialise()

    assert 'preserveAspectRatio="xMinYMin meet"' in xml
    assert "shape-rendering: geometricPrecision;" in xml


def test_xml_polygon_points(svg_maker, snapshot):
    polygons_and_colours = [
        {
            "polygon": [[(0, 0), (10, 0), (10, 10)], [(2, 2), (8, 2), (8, 8)]],
            "broken": False,
            "colour": [(65, 124, 192, 1), (255, 255, 255, 0.5)],
        }
    ]

    assert svg_maker.xml_polygon_points(polygons_and_colours) == snapshot


def test_xml_polygon_points_passes_through_substituted_images(svg_maker):
    polygons_and_colours = [
        {
            "polygon": ["<g>image</g>"],
            "broken": True,
            "colour": [(0, 0, 0, 1)],
        }
    ]

    assert svg_maker.xml_polygon_points(polygons_and_colours) == "<g><g>image</g></g>"


def test_xml_result_replaces_placeholder(svg_maker, snapshot):
    polygons_and_colours = [
        {
            "polygon": [[(0, 0), (10, 0), (10, 10)]],
            "broken": False,
            "colour": [(65, 124, 192, 1)],
        }
    ]

    result = svg_maker.xml_result(polygons_and_colours)

    assert svg_maker.poly_placeholder not in result
    assert normalise_svg(result) == snapshot


def test_xml_setup_pattern_grid(pattern_svg_maker, snapshot):
    pattern = pattern_svg_maker.xml_setup_pattern()

    assert round_nested(pattern) == snapshot


def broken_elements(preset) -> list:
    """
    Positions of the elements marked as broken in a pattern.
    """

    pattern = SVGmaker(preset, [200, 200]).xml_setup_pattern()

    return [
        (row, column)
        for row, columns in enumerate(pattern)
        for column, element in enumerate(columns)
        if element[2]["broken"]
    ]


def candidate_elements(preset) -> list:
    """
    Positions eligible to break, i.e. everything that is not an edge.
    """

    pattern = SVGmaker(preset, [200, 200]).xml_setup_pattern()

    return [
        (row, column)
        for row, columns in enumerate(pattern)
        for column, element in enumerate(columns)
        if not element[2]["edge"] and not element[2]["invisible_edge"]
    ]


def test_xml_setup_pattern_marks_broken_elements(broken_pattern_preset):
    broken = broken_elements(broken_pattern_preset)
    candidates = candidate_elements(broken_pattern_preset)

    assert broken
    # A real sample: some candidates break, not all of them. At a high factor
    # the amount is clamped to the candidate count and nothing is left to pick.
    assert len(broken) < len(candidates)
    assert set(broken) <= set(candidates)


def test_xml_setup_pattern_skips_edges(broken_pattern_preset):
    pattern = SVGmaker(broken_pattern_preset, [200, 200]).xml_setup_pattern()

    assert all(
        not element[2]["edge"]
        for columns in pattern
        for element in columns
        if element[2]["broken"]
    )


def test_xml_setup_pattern_can_break_edges(broken_pattern_preset):
    broken_pattern_preset["pattern"]["broken"]["skip_edge"] = False
    broken_pattern_preset["pattern"]["broken"]["factor"] = 0.5

    pattern = SVGmaker(broken_pattern_preset, [200, 200]).xml_setup_pattern()

    assert any(
        element[2]["edge"]
        for columns in pattern
        for element in columns
        if element[2]["broken"]
    )


def test_xml_setup_pattern_is_seeded(broken_pattern_preset):
    first = broken_elements(broken_pattern_preset)
    second = broken_elements(broken_pattern_preset)

    assert first == second


def test_xml_setup_pattern_differs_per_seed(broken_pattern_preset):
    first = broken_elements({**broken_pattern_preset, "seed": 42})
    second = broken_elements({**broken_pattern_preset, "seed": 7})

    assert first != second


def test_xml_setup_pattern_without_seed_is_not_reproducible(broken_pattern_preset):
    """
    Guards the fixtures: the snapshots only hold because a `seed` is set.
    """

    del broken_pattern_preset["seed"]

    # 3 out of 7 candidates break, so 20 unseeded runs returning one and the
    # same set is not a realistic outcome.
    results = {tuple(broken_elements(broken_pattern_preset)) for _ in range(20)}

    assert len(results) > 1


def test_xml_create_pattern_joins_rows(svg_maker):
    rows = [
        [
            {
                "polygon": [[(0, 0), (10, 0), (10, 10)]],
                "broken": False,
                "colour": [(0, 0, 0, 1)],
            }
        ]
    ]

    result = svg_maker.xml_create_pattern(rows)

    assert len(result["paths"]) == 1
    assert result["string"] == result["paths"][0]


def test_prepare_output_path_for_directory(svg_maker, tmp_path):
    output = svg_maker.prepare_output_path(tmp_path / "preset.json", tmp_path, "svg")

    assert output == tmp_path / "preset.svg"


def test_prepare_output_path_for_file(svg_maker, tmp_path):
    output = svg_maker.prepare_output_path(
        tmp_path / "preset.json", tmp_path / "custom.svg", "png"
    )

    assert output == tmp_path / "custom.png"


def test_prepare_output_path_with_prefix(svg_maker, tmp_path):
    output = svg_maker.prepare_output_path(
        tmp_path / "preset.json", tmp_path, "svg", False, "seigaiha"
    )

    assert output == tmp_path / "preset_seigaiha.svg"


def test_prepare_output_path_with_unique_filename(svg_maker, tmp_path):
    # Note: unlike the other branches this returns a `str`, not a `Path`.
    output = svg_maker.prepare_output_path(
        tmp_path / "preset.json", tmp_path, "svg", True
    )

    assert re.fullmatch(
        r"preset_\d{2}-\d{2}-\d{4}_\d{2}-\d{2}-\d{2}-\d{6}\.svg",
        Path(output).name,
    )


def test_save_svg_writes_file(svg_maker, tmp_path):
    target = tmp_path / "out.svg"

    svg_maker.save_svg("<svg></svg>", target)

    assert target.read_text() == "<svg></svg>"


def test_save_png_renders_image(svg_maker, tmp_path):
    target = tmp_path / "out.png"

    svg_maker.save_png(svg_maker.xml_result([]), target)

    assert target.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n"


def test_determine_external_svg_dimensions(svg_maker):
    result = svg_maker._determine_external_svg_dimensions(EXTERNAL_SVG)

    assert result["width"] == 60.0
    assert result["height"] == 40.0
    assert result["svg"] == EXTERNAL_SVG


def test_determine_external_svg_dimensions_falls_back_to_view_box(svg_maker):
    result = svg_maker._determine_external_svg_dimensions(
        EXTERNAL_SVG_WITHOUT_DIMENSIONS
    )

    assert result["width"] == 60.0
    assert result["height"] == 40.0
    assert 'width="60"' in result["svg"]
    assert 'height="40"' in result["svg"]


def test_extract_svg_part_strips_prolog(svg_maker):
    assert svg_maker._extract_svg_part(EXTERNAL_SVG).startswith("<svg")


def test_extract_svg_part_raises_without_svg_tag(svg_maker):
    with pytest.raises(Exception, match="Could not extract"):
        svg_maker._extract_svg_part("<html></html>")


def test_broken_images_are_wrapped_in_a_transform_group(broken_pattern_preset):
    encoded = base64.b64encode(EXTERNAL_SVG.encode("utf-8")).decode("utf-8")
    broken_pattern_preset["pattern"]["broken"]["images"] = [encoded]

    svg_maker = SVGmaker(broken_pattern_preset, [200, 200])

    assert len(svg_maker.repeat_broken_images) == 1
    assert svg_maker.repeat_broken_images[0].startswith('<g transform="matrix(')
    assert "%posX%" in svg_maker.repeat_broken_images[0]
    assert "%posY%" in svg_maker.repeat_broken_images[0]
