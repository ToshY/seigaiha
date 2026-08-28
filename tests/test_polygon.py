import math

import pytest
from shapely.geometry import Polygon  # type: ignore[import-untyped]

from seigaiha.cli import (
    check_polygon_boundary_limit,
    create_polygon,
    create_polygon_object,
    get_colours,
    get_polygon_boundary,
    get_polygon_coordinates,
    get_polygon_dimensions,
    get_polygon_points,
    rotate_polygon,
    scale_polygon,
    translate_polygon,
)
from tests.conftest import round_nested


@pytest.mark.parametrize("corners", [3, 4, 7, 36])
def test_get_polygon_points_returns_point_per_corner(corners):
    points = get_polygon_points(corners, 100)

    assert len(points) == corners


def test_get_polygon_points_starts_at_top_center():
    points = get_polygon_points(4, 100)

    assert round_nested(points[0]) == [50.0, 0.0]


def test_get_polygon_points_lie_on_the_circumference():
    radius = 50
    points = get_polygon_points(9, radius * 2)

    for x_coordinate, y_coordinate in points:
        distance = math.hypot(x_coordinate - radius, y_coordinate - radius)
        assert distance == pytest.approx(radius)


def test_create_polygon_object_builds_closed_polygon():
    polygon = create_polygon_object(get_polygon_points(4, 100))

    assert isinstance(polygon, Polygon)
    assert polygon.is_valid
    assert polygon.area == pytest.approx(5000)


def test_get_polygon_coordinates_drops_closing_point_for_collection():
    polygons = [create_polygon_object(get_polygon_points(4, 100))]

    coordinates = get_polygon_coordinates(polygons)

    assert len(coordinates) == 1
    assert len(coordinates[0]) == 4


def test_get_polygon_coordinates_for_single_polygon():
    polygon = create_polygon_object(get_polygon_points(6, 100))

    assert len(get_polygon_coordinates(polygon)) == 6


def test_get_colours_cycles_until_every_polygon_is_covered():
    polygons = [None] * 5

    assert get_colours(polygons, ["a", "b"]) == ["a", "b", "a", "b", "a"]


def test_get_colours_keeps_colours_when_enough_are_given():
    polygons = [None] * 2

    assert get_colours(polygons, ["a", "b", "c"]) == ["a", "b", "c"]


def test_translate_polygon_moves_bounds():
    polygon = create_polygon_object(get_polygon_points(4, 100))

    translated = translate_polygon(polygon, 10, -5)

    assert round_nested(list(get_polygon_boundary(translated))) == [
        10.0,
        -5.0,
        110.0,
        95.0,
    ]


def test_rotate_polygon_preserves_area():
    polygon = create_polygon_object(get_polygon_points(6, 100))

    rotated = rotate_polygon(polygon, 30)

    assert rotated.area == pytest.approx(polygon.area)
    assert rotated.bounds != polygon.bounds


def test_scale_polygon_scales_area_quadratically():
    polygon = create_polygon_object(get_polygon_points(4, 100))

    scaled = scale_polygon(polygon, 2)

    assert scaled.area == pytest.approx(polygon.area * 4)


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (0.0, 0),
        (5.0, 5),
        # Within the boundary limit of a whole number, so snapped to it.
        (4.9999999, 5),
        # A fraction above .5 rounds up, anything below is kept as is.
        (5.6, 6),
        (5.4, 5.4),
    ],
)
def test_check_polygon_boundary_limit(value, expected):
    assert check_polygon_boundary_limit(value) == expected


def test_get_polygon_dimensions_is_order_independent():
    assert get_polygon_dimensions(10, 20, 0, 0) == {"width": 10, "height": 20}
    assert get_polygon_dimensions(0, 0, 10, 20) == {"width": 10, "height": 20}


@pytest.mark.parametrize(
    ("edges", "fractions", "rotation"),
    [
        (4, 5, 0),
        (6, 4, 0),
        (7, 5, 30),
    ],
    ids=["square-odd-fractions", "hexagon-even-fractions", "heptagon-rotated"],
)
def test_create_polygon(edges, fractions, rotation, colours, snapshot):
    colour_tuples = [tuple(colour.values()) for colour in colours]

    boundary_box, polygons, coordinates, polygon_colours = create_polygon(
        edges, fractions, colour_tuples, 100, 0.3, rotation
    )

    assert {
        "boundary_box": round_nested(boundary_box),
        "polygon_count": len(polygons),
        "coordinates": round_nested(coordinates),
        "colours": polygon_colours,
    } == snapshot


@pytest.mark.parametrize(
    ("fractions", "expected"),
    [(3, 4), (4, 4), (5, 6), (6, 6)],
)
def test_create_polygon_drops_last_slice_for_even_fractions(
    colours, fractions, expected
):
    """
    An odd amount of fractions yields `fractions + 1` slices; an even amount
    drops the last (zero pixel) slice, so it yields `fractions`.
    """

    colour_tuples = [tuple(colour.values()) for colour in colours]

    _, polygons, _, _ = create_polygon(6, fractions, colour_tuples, 100, 0.3, 0)

    assert len(polygons) == expected


def test_create_polygon_rescales_rotated_polygon_to_requested_width(colours):
    colour_tuples = [tuple(colour.values()) for colour in colours]

    boundary_box, _, _, _ = create_polygon(7, 5, colour_tuples, 100, 0.3, 45)

    assert boundary_box["width"] == pytest.approx(100)


def test_create_polygon_without_spacing(colours, snapshot):
    colour_tuples = [tuple(colour.values()) for colour in colours]

    _, _, coordinates, _ = create_polygon(4, 4, colour_tuples, 100, None, 0)

    assert round_nested(coordinates) == snapshot


def test_create_polygon_assigns_a_colour_to_every_slice(colours):
    colour_tuples = [tuple(colour.values()) for colour in colours]

    _, polygons, _, polygon_colours = create_polygon(6, 9, colour_tuples, 100, 0.3, 0)

    assert len(polygon_colours) == len(polygons)
