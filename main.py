# -*- coding: utf-8 -*-

import argparse
import math
from pathlib import Path
from src.banner import cli_banner
from src.args import InputCheck
from shapely.geometry import Polygon, Point
from shapely import affinity
from src.svg import SVGmaker
from src.general import read_json_from_file, read_json_from_string
from itertools import cycle
from rich import print


def cli_args():
    """
    Command Line argument parser.

    Returns
    -------
    list
        List of dictionaries of seigaiha presets.

    """

    # Arguments
    parser = argparse.ArgumentParser(description=__doc__)
    # noinspection PyTypeChecker
    parser.add_argument(
        "-p",
        "--preset",
        type=str,
        required=True,
        action=InputCheck,
        const=False,
        nargs="+",
        help="Path to JSON file or string with preset options",
    )

    args = parser.parse_args()

    user_args = input_arguments(args.preset)

    return user_args


def input_arguments(presets: list):
    """
    Check the presets.

    Parameters
    ----------
    presets : list
        Input preset argument(s).

    Returns
    -------
    None.

    """

    outputs = [{"type": "directory", "value": Path(output_directory).resolve()}]

    len_presets = len(presets)
    len_outputs = len(outputs)

    if len_presets != len_outputs:
        if len_outputs != 1:
            raise Exception(
                f"[red]Amount of preset arguments ({len_presets}) "
                f"does not equal the amount of output arguments ({len_outputs})."
            )

    # Prepare inputs/outputs/presets
    batch = {}
    for element_index, element in enumerate(presets):
        data = {}
        file_path = element["value"]
        data_type = element["type"]

        if data_type == "json":
            data = read_json_from_string(file_path)
        elif data_type == "file":
            data = read_json_from_file(file_path)

        if len_outputs == 1:
            output_files = [[*outputs][0]]
        else:
            output_files = outputs[0]
            outputs.pop(0)

        batch[str(element_index)] = {
            "input": [
                {
                    "type": data_type,
                    "value": [file_path],
                }
            ],
            "data": data,
            "output": output_files,
        }

    return batch


def get_polygon_points(corners: int, width: int) -> list:
    """
    Get coordinates for the polygon.

    Parameters
    ----------
    corners: int
        Amount of corner points for the polygon.
    width: int
        The width/radius of the polygon.
    Returns
    -------
    list
        Points of the polygon.
    """

    radius = width / 2
    points = []
    for k in range(corners):
        x = radius + (
            radius * math.cos(((2 * math.pi * k) / corners) - (1 / 2 * math.pi))
        )
        y = radius + (
            radius * math.sin(((2 * math.pi * k) / corners) - (1 / 2 * math.pi))
        )
        points.append((x, y))

    return points


def create_polygon_object(points: list) -> Polygon:
    """
    Return a Shapely polygon from points.

    Parameters
    ----------
    points : list
        List of coordinates to create a Shapely Polygon.

    Returns
    -------
    Polygon
        Shapely Polygon object.
    """
    return Polygon([[p[0], p[1]] for p in points])


def get_polygon_coordinates(polygon_collection) -> list:
    """
    Return polygon coordinates for given collection of polygons.

    Parameters
    ----------
    polygon_collection : list
        A collection of Polygons.

    Returns
    -------
    list
        A collection of exterior coordinates of each Polygon.
    """

    if type(polygon_collection) is list:
        coordinates = []
        for polygon in polygon_collection:
            if type(polygon) is Point:
                coordinates.append(polygon.coords[:-1])
            else:
                coordinates.append(polygon.exterior.coords[:-1])
        return coordinates

    return list(polygon_collection.exterior.coords)[:-1]


def get_colours(polygon_collection: list, polygon_colours: list):
    """
    Get alternating colours for polygon filling.

    Parameters
    ----------
    polygon_collection : list
        A collection of Shapely Polygon objects.
    polygon_colours : list
        A collection of RGB colours.
    Returns
    -------
    list
        Collection of colours to patch the polygon with.
    """

    polygon_count = len(polygon_collection)
    if len(polygon_colours) < polygon_count:
        colour_cycle = cycle(polygon_colours)
        colour_repeat_collection = []
        for i in range(0, polygon_count):
            colour_repeat_collection.append(next(colour_cycle))

        return colour_repeat_collection

    return polygon_colours


def translate_polygon(
    polygon: Polygon, x_direction: float, y_direction: float
) -> Polygon:
    """
    Returns translated polygon with specified x/y offset.

    Parameters
    ----------
    polygon : Polygon
        Shapely Polygon object.
    x_direction : float
        X offset direction.
    y_direction : float
        Y offset direction.

    Returns
    -------
    Polygon
        Translated Polygon.

    """
    return affinity.translate(polygon, x_direction, y_direction)


def rotate_polygon(polygon: Polygon, rotation: int) -> Polygon:
    """
    Returns rotated polygon.

    Parameters
    ----------
    polygon : Polygon
        Polygon to be rotated.
    rotation : int
        Rotation in degrees.

    Returns
    -------
    Polygon
        Rotated Polygon.
    """
    return affinity.rotate(polygon, rotation, origin="centroid")


def scale_polygon(polygon: Polygon, scale_factor: float) -> Polygon:
    """
    Returns scaled polygon with specified scale factor.

    Parameters
    ----------
    polygon : Polygon
        Polygon to be scaled.
    scale_factor : float
        Scaling factor.

    Returns
    -------
    Polygon
        Scaled Polygon.
    """
    return affinity.scale(
        polygon, xfact=scale_factor, yfact=scale_factor, origin="center"
    )


def check_polygon_boundary_limit(value: float, limit: float = 0.1e-5) -> float:
    """
    Returns the checked value for polygon boundary.

    Parameters
    ----------
    value : float
        Value to check.
    limit : float, optional
        The limit to which extent it is acceptable to assume rounding issues. The default is 0.1e-5.
    Returns
    -------
    float
        The initial value, possibly rounded.
    """
    if value < (round(value) + limit):
        return round(value)

    return value


def get_polygon_boundary(polygon: Polygon) -> list:
    """
    Returns the bounds of a polygon.

    Parameters
    ----------
    polygon : Polygon
        Polygon to get the boundaries.

    Returns
    -------
    list
        The boundaries of the Polygon.
    """
    return polygon.bounds


def get_polygon_dimensions(x1: float, y1: float, x2: float, y2: float) -> dict:
    """

    Parameters
    ----------
    x1 : float
        X1 of Polygon.
    y1 : float
        Y1 of Polygon.
    x2 : float
        X2 of Polygon.
    y2 : float
        Y2 of Polygon.

    Returns
    -------
    dict
        Dictionary with the width and height of box which Polygon fits.
    """
    return {
        "width": max([x1, x2]) - min([x1, x2]),
        "height": max([y1, y2]) - min([y1, y2]),
    }


def create_polygon(
    polygon_corners,
    polygon_fractions,
    polygon_colours,
    polygon_width,
    spacing=0.5,
    polygon_rotation=0,
):
    """Create a single polygon"""

    # Get polygon points
    all_points = get_polygon_points(polygon_corners, polygon_width)

    # Get polygon object
    polygon = create_polygon_object(all_points)

    # Retrieve polygon boundary box coordinates
    x1, y1, x2, y2 = get_polygon_boundary(polygon)
    boundary_box = get_polygon_dimensions(x1, y1, x2, y2)

    # Rotate
    if polygon_rotation != 0:
        # Rotate
        polygon = rotate_polygon(polygon, polygon_rotation)
        x1, y1, x2, y2 = get_polygon_boundary(polygon)

        # Retranslate
        polygon = translate_polygon(polygon, -x1, -y1)

        x1, y1, x2, y2 = get_polygon_boundary(polygon)
        boundary_box = get_polygon_dimensions(x1, y1, x2, y2)

    # Check if needs rescaling and translating
    if (
        check_polygon_boundary_limit(x1) != 0
        or check_polygon_boundary_limit(y1) != 0
        or check_polygon_boundary_limit(x2) != polygon_width
    ):
        # Scale
        rescale_factor = polygon_width / boundary_box["width"]
        polygon = scale_polygon(polygon, rescale_factor)

        x1, y1, x2, y2 = get_polygon_boundary(polygon)
        polygon = translate_polygon(polygon, -x1, -y1)

        x1, y1, x2, y2 = get_polygon_boundary(polygon)
        boundary_box = get_polygon_dimensions(x1, y1, x2, y2)

    # Get center coordinates of polygon
    px_center = polygon.centroid.x
    py_center = polygon.centroid.y

    # Get new coordinates for all points
    all_points = get_polygon_coordinates(polygon)

    # Fractions list
    if spacing is not None:
        fractions = []
        for i, v in enumerate(list(range(1, polygon_fractions + 1))):
            if (i % 2) != 0:
                fractions.append((v / polygon_fractions))
                continue

            vl = (v / polygon_fractions) - (spacing) * 1 / polygon_fractions
            fractions.append(vl if vl <= 1 else 1)
    else:
        fractions = [
            v / polygon_fractions for v in list(range(1, polygon_fractions + 1))
        ]

    # Create all (sub)polygons
    vct = []
    for point in all_points:
        pxl = [
            (
                (px_center - point[0]) * x + point[0],
                (py_center - point[1]) * x + point[1],
            )
            for x in fractions
        ]
        vct.append([point] + pxl)

    # Create polygons
    polygon_collection = [Polygon(elk) for elk in zip(*vct)]

    # If even, remove the last unnecessary entry (0 pixels)
    if polygon_fractions % 2 == 0:
        polygon_collection = polygon_collection[:-1]

    # Get coords back
    polygon_coordinates = get_polygon_coordinates(polygon_collection)

    # Get colours to fill
    polygon_colours = get_colours(polygon_collection, polygon_colours)

    return [boundary_box, polygon_collection, polygon_coordinates, polygon_colours]


def main():
    # Input arguments
    presets = cli_args()

    # Iterate over presets
    for item_index, item in presets.items():
        for current_file_index, _ in enumerate(item["input"]):
            # Check if first/last item for reporting
            output = item["output"][current_file_index]["value"]
            data = item["data"]
            width = data["width"]
            fractions = data["fractions"]
            edges = data["edges"]
            spacing = data["spacing"]
            rotation = data["rotation"]
            pattern = data["pattern"]
            colours = data["colours"]

            # Colours to tuple
            colours = [tuple(el.values()) for el in colours]

            # Create polygon object
            box_dims, polygon_objects, polygon_coords, colours_format = create_polygon(
                edges, fractions, colours, width, spacing, rotation
            )

            # Init SVGmaker
            SVG = SVGmaker(data, output, [box_dims["width"], box_dims["height"]])

            # Create single SVG string
            svg_str = SVG.xml_init()
            svg_poly = SVG.xml_poly(
                [{"polygon": polygon_coords, "broken": False, "colour": colours_format}]
            )
            svg_finalized = svg_str.replace(SVG.poly_placeholder, svg_poly)

            # Save and print
            print(
                "\r > Saved polygon to [cyan]{}[/cyan] & [cyan]{}[/cyan]".format(
                    SVG.save_svg(svg_finalized), SVG.save_png(svg_finalized)
                )
            )

            # Create pattern
            if pattern:
                # Init pattern
                svg_str_pattern = SVG.xml_init_pattern()

                # Check broken
                broken_pattern = data["repeat"]["broken"]

                if not all(
                    key in broken_pattern for key in ("factor", "fractions", "colours")
                ):
                    raise Exception(
                        "Not all necessary keys `factor`, `fractions` and `colours` for broken "
                        "pattern are specified."
                    )

                if broken_pattern["fractions"] >= fractions:
                    raise Exception(
                        "The `fractions` key for broken pattern can not be equal or larger than "
                        "the main `fractions` key."
                    )

                if len(broken_pattern["colours"]) != broken_pattern["fractions"]:
                    raise Exception(
                        "The amount of colours for the broken pattern has to be the same as "
                        "specified broken `fractions`."
                    )

                # Create pattern setup
                svg_pattern = SVG.xml_setup_pattern(data["repeat"])

                # Prepare broken polygon and colours
                broken_polygon = polygon_objects[: broken_pattern["fractions"]]
                broken_colours_tuple = [
                    tuple(el.values()) for el in broken_pattern["colours"]
                ]
                broken_colours_format = get_colours(
                    broken_polygon, broken_colours_tuple
                )

                # Create copies of the initial "single" polygon and translate conform pattern
                pattern_polygons_objects = []
                for idx, row in enumerate(svg_pattern):
                    pattern_polygons_objects.append([])
                    polygons_row_objects = []
                    for ix, xl in enumerate(row):
                        xp = xl[0]
                        yp = xl[1]
                        is_broken = xl[2]["broken"]
                        if is_broken is True:
                            single_polygon = broken_polygon
                        else:
                            single_polygon = polygon_objects

                        transformed_polygon = [
                            affinity.translate(p, xp, yp) for p in single_polygon
                        ]

                        polygons_row_objects.append(
                            {"polygon": transformed_polygon, "broken": is_broken}
                        )

                    pattern_polygons_objects[idx] = polygons_row_objects

                pattern_polygons_objects_copy = pattern_polygons_objects.copy()
                first_polygon_bounds = pattern_polygons_objects[0][0]["polygon"][
                    0
                ].bounds
                last_polygon_bounds = pattern_polygons_objects[-1][-1]["polygon"][
                    -1
                ].bounds

                polygon_width = first_polygon_bounds[2] - first_polygon_bounds[0]
                polygon_height = first_polygon_bounds[3] - first_polygon_bounds[1]

                pattern_container = [
                    (
                        first_polygon_bounds[0] + (polygon_width / 2),
                        first_polygon_bounds[1] + (polygon_height / 2),
                    ),
                    (
                        first_polygon_bounds[0] + (polygon_width / 2),
                        last_polygon_bounds[3],
                    ),
                    (
                        last_polygon_bounds[2],
                        last_polygon_bounds[3],
                    ),
                    (
                        last_polygon_bounds[2],
                        first_polygon_bounds[1] + (polygon_height / 2),
                    ),
                ]
                pattern_polygon_container = Polygon(pattern_container)

                pattern_polygon_coordinates = []
                is_empty_counter = 0
                for idx, row in enumerate(pattern_polygons_objects):
                    pattern_polygon_coordinates.append([])
                    polygons_row_new = []
                    for idy, col in enumerate(row):
                        for idp, spol in enumerate(col["polygon"]):
                            intersect = spol.intersection(pattern_polygon_container)
                            if not intersect.is_empty:
                                pattern_polygons_objects_copy[idx][idy]["polygon"][
                                    idp
                                ] = intersect
                            else:
                                is_empty_counter += 1

                        single_polygon_coords_new = get_polygon_coordinates(
                            pattern_polygons_objects_copy[idx][idy]["polygon"]
                        )

                        is_broken = pattern_polygons_objects[idx][idy]["broken"]
                        polygons_row_new.append(
                            {
                                "polygon": single_polygon_coords_new,
                                "broken": is_broken,
                                "colour": colours_format
                                if not is_broken
                                else broken_colours_format,
                            }
                        )

                    pattern_polygon_coordinates[idx] = polygons_row_new

                # Create the actual pattern
                svg_poly_pattern = SVG.xml_create_pattern(pattern_polygon_coordinates)
                svg_finalized_pattern = svg_str_pattern.replace(
                    SVG.poly_placeholder, svg_poly_pattern["string"]
                )

                # Save and print
                print(
                    "\r > Saved pattern to [cyan]{}[/cyan] & [cyan]{}[/cyan]".format(
                        SVG.save_svg(svg_finalized_pattern),
                        SVG.save_png(svg_finalized_pattern),
                    )
                )

                return [
                    pattern_container,
                    pattern_polygon_container,
                    pattern_polygons_objects,
                    pattern_polygon_coordinates,
                ]


if __name__ == "__main__":
    """Main"""
    cli_banner("Seigaiha")

    # Stop execution at keyboard input
    try:
        output_directory = "./output"
        preset_directory = "./preset"

        svgs = main()
    except KeyboardInterrupt:
        print("\r\n\r\n> [red]Execution cancelled by user[/red]")
        exit()
