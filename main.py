"""
@author: ToshY
"""

import random
import argparse
import math
import sys
from pathlib import Path
from itertools import cycle
from rich import print
from shapely.geometry import Polygon, Point, LineString
from shapely import affinity
from src.args import InputCheck
from src.banner import cli_banner
from src.svg import SVGmaker
from src.general import read_json_from_file, read_json_from_string


def cli_args():
    """
    Command Line argument parser.
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
    """

    outputs = [{"type": "directory", "value": Path(OUTPUT_DIRECTORY).resolve()}]

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
    """

    radius = width / 2
    points = []
    for k in range(corners):
        x_coordinate = radius + (
            radius * math.cos(((2 * math.pi * k) / corners) - (1 / 2 * math.pi))
        )
        y_coordinate = radius + (
            radius * math.sin(((2 * math.pi * k) / corners) - (1 / 2 * math.pi))
        )
        points.append((x_coordinate, y_coordinate))

    return points


def create_polygon_object(points: list) -> Polygon:
    """
    Return a Shapely polygon from points.
    """
    return Polygon([[p[0], p[1]] for p in points])


def get_polygon_coordinates(polygon_collection) -> list:
    """
    Return polygon coordinates for given collection of polygons.
    """

    if isinstance(polygon_collection, list):
        coordinates = []
        for polygon in polygon_collection:
            if isinstance(polygon, (Point, LineString)):
                coordinates.append(polygon.coords[:-1])
            else:
                coordinates.append(polygon.exterior.coords[:-1])
        return coordinates

    return list(polygon_collection.exterior.coords)[:-1]


def get_colors(polygon_collection: list, polygon_colors: list):
    """
    Get alternating colors for polygon filling.
    """

    polygon_count = len(polygon_collection)
    if len(polygon_colors) < polygon_count:
        color_cycle = cycle(polygon_colors)
        color_repeat_collection = []
        for _ in range(0, polygon_count):
            color_repeat_collection.append(next(color_cycle))

        return color_repeat_collection

    return polygon_colors


def translate_polygon(
    polygon: Polygon, x_direction: float, y_direction: float
) -> Polygon:
    """
    Returns translated polygon with specified x/y offset.
    """
    return affinity.translate(polygon, x_direction, y_direction)


def rotate_polygon(polygon: Polygon, rotation: int) -> Polygon:
    """
    Returns rotated polygon.
    """
    return affinity.rotate(polygon, rotation, origin="centroid")


def scale_polygon(polygon: Polygon, scale_factor: float) -> Polygon:
    """
    Returns scaled polygon with specified scale factor.
    """
    return affinity.scale(
        polygon, xfact=scale_factor, yfact=scale_factor, origin="center"
    )


def check_polygon_boundary_limit(value: float, limit: float = 0.1e-5) -> float:
    """
    Returns the checked value for polygon boundary.
    """
    if value < (round(value) + limit):
        return round(value)

    return value


def get_polygon_boundary(polygon: Polygon) -> list:
    """
    Returns the bounds of a polygon.
    """
    return polygon.bounds


def get_polygon_dimensions(
    x_coordinate_1: float,
    y_coordinate_1: float,
    x_coordinate_2: float,
    y_coordinate_2: float,
) -> dict:
    """
    Get Polygon dimensions.
    """
    return {
        "width": max([x_coordinate_1, x_coordinate_2])
        - min([x_coordinate_1, x_coordinate_2]),
        "height": max([y_coordinate_1, y_coordinate_2])
        - min([y_coordinate_1, y_coordinate_2]),
    }


def create_polygon(
    polygon_corners,
    polygon_fractions,
    polygon_colors,
    polygon_width,
    spacing=0.5,
    polygon_rotation=0,
):
    """
    Create a single polygon.
    """

    # Get polygon points
    all_points = get_polygon_points(polygon_corners, polygon_width)

    # Get polygon object
    polygon = create_polygon_object(all_points)

    # Retrieve polygon boundary box coordinates
    (
        x_coordinate_1,
        y_coordinate_1,
        x_coordinate_2,
        y_coordinate_2,
    ) = get_polygon_boundary(polygon)
    boundary_box = get_polygon_dimensions(
        x_coordinate_1, y_coordinate_1, x_coordinate_2, y_coordinate_2
    )

    # Rotate
    if polygon_rotation != 0:
        # Rotate
        polygon = rotate_polygon(polygon, polygon_rotation)
        (
            x_coordinate_1,
            y_coordinate_1,
            x_coordinate_2,
            y_coordinate_2,
        ) = get_polygon_boundary(polygon)

        # Retranslate
        polygon = translate_polygon(polygon, -x_coordinate_1, -y_coordinate_1)

        (
            x_coordinate_1,
            y_coordinate_1,
            x_coordinate_2,
            y_coordinate_2,
        ) = get_polygon_boundary(polygon)
        boundary_box = get_polygon_dimensions(
            x_coordinate_1, y_coordinate_1, x_coordinate_2, y_coordinate_2
        )

    # Check if needs rescaling and translating
    if (
        check_polygon_boundary_limit(x_coordinate_1) != 0
        or check_polygon_boundary_limit(y_coordinate_1) != 0
        or check_polygon_boundary_limit(x_coordinate_2) != polygon_width
    ):
        # Scale
        rescale_factor = polygon_width / boundary_box["width"]
        polygon = scale_polygon(polygon, rescale_factor)

        (
            x_coordinate_1,
            y_coordinate_1,
            x_coordinate_2,
            y_coordinate_2,
        ) = get_polygon_boundary(polygon)
        polygon = translate_polygon(polygon, -x_coordinate_1, -y_coordinate_1)

        (
            x_coordinate_1,
            y_coordinate_1,
            x_coordinate_2,
            y_coordinate_2,
        ) = get_polygon_boundary(polygon)
        boundary_box = get_polygon_dimensions(
            x_coordinate_1, y_coordinate_1, x_coordinate_2, y_coordinate_2
        )

    # Get center coordinates of polygon
    px_center = polygon.centroid.x
    py_center = polygon.centroid.y

    # Get new coordinates for all points
    all_points = get_polygon_coordinates(polygon)

    # Fractions list
    if spacing is not None:
        fractions = []
        for i, fraction_value in enumerate(list(range(1, polygon_fractions + 1))):
            if (i % 2) != 0:
                fractions.append((fraction_value / polygon_fractions))
                continue

            val = (fraction_value / polygon_fractions) - spacing * 1 / polygon_fractions
            fractions.append(val if val <= 1 else 1)
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

    # Get colors to fill
    polygon_colors = get_colors(polygon_collection, polygon_colors)

    return [boundary_box, polygon_collection, polygon_coordinates, polygon_colors]


def main():
    """
    Main
    """
    presets = cli_args()

    # Iterate over presets
    for _, item in presets.items():
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
            colors = data["colors"]

            # colors to tuple
            colors = [tuple(el.values()) for el in colors]

            # Create polygon object
            box_dims, polygon_objects, polygon_coords, colors_format = create_polygon(
                edges, fractions, colors, width, spacing, rotation
            )

            # Init SVGmaker
            svg_maker = SVGmaker(data, output, [box_dims["width"], box_dims["height"]])

            # Create single SVG string
            svg_str = svg_maker.xml_init()
            svg_poly = svg_maker.xml_poly(
                [{"polygon": polygon_coords, "broken": False, "color": colors_format}]
            )
            svg_finalized = svg_str.replace(svg_maker.poly_placeholder, svg_poly)

            # Save and print
            print(
                f"\r > Saved polygon to [cyan]{svg_maker.save_svg(svg_finalized)}[/cyan] & [cyan]{svg_maker.save_png(svg_finalized)}[/cyan]"
            )

            # Create pattern
            if pattern:
                svg_str_pattern = svg_maker.xml_init_pattern()
                svg_pattern = svg_maker.xml_setup_pattern()

                # "Broken" polygon should be a "normal" polygon if a broken pattern is not specified
                broken_polygon = polygon_objects[:fractions]

                broken_pattern = data["repeat"]["broken"]
                if broken_pattern:
                    # Prepare broken polygon and colors
                    broken_colors_tuple = [
                        tuple(el.values()) for el in broken_pattern["colors"]
                    ]

                    _, broken_polygon_objects, _, broken_colors_format = create_polygon(
                        edges,
                        broken_pattern["fractions"],
                        broken_colors_tuple,
                        width,
                        spacing,
                        rotation,
                    )

                    broken_polygon = broken_polygon_objects[
                        : broken_pattern["fractions"]
                    ]

                # Create copies of the initial "single" polygon and translate conform pattern
                pattern_polygons_objects = []
                for idx, row in enumerate(svg_pattern):
                    pattern_polygons_objects.append([])
                    polygons_row_objects = []
                    for _, current_x_list in enumerate(row):
                        x_point = current_x_list[0]
                        y_point = current_x_list[1]
                        is_broken = current_x_list[2]["broken"]

                        single_polygon = polygon_objects
                        if is_broken is True:
                            single_polygon = broken_polygon

                        transformed_polygon = [
                            affinity.translate(p, x_point, y_point)
                            for p in single_polygon
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

                        single_polygon_coords_new = get_polygon_coordinates(
                            pattern_polygons_objects_copy[idx][idy]["polygon"]
                        )

                        is_broken = pattern_polygons_objects[idx][idy]["broken"]

                        if is_broken and svg_maker.repeat_broken_images:
                            pos_x_offset = svg_maker.width / 2
                            if idx & 1:
                                pos_x_offset = svg_maker.width

                            single_polygon_coords_new.append(
                                random.choice(svg_maker.repeat_broken_images)
                                .replace(
                                    "%posX%",
                                    str(
                                        (
                                            svg_maker.width
                                            * svg_maker.repeat_horizontal_spacing
                                            * idy
                                        )
                                        + pos_x_offset
                                    ),
                                )
                                .replace(
                                    "%posY%",
                                    str(
                                        (
                                            svg_maker.height
                                            * svg_maker.repeat_vertical_spacing
                                            * idx
                                        )
                                        + (svg_maker.height / 2)
                                    ),
                                )
                            )

                        polygons_row_new.append(
                            {
                                "polygon": single_polygon_coords_new,
                                "broken": is_broken,
                                "color": colors_format
                                if not is_broken
                                else broken_colors_format,
                            }
                        )

                    # If odd row in pattern, last element is unnecessary and was not correctly intersected earlier.
                    if idx & 1:
                        polygons_row_new = polygons_row_new[:-1]

                    pattern_polygon_coordinates[idx] = polygons_row_new

                # Create the actual pattern
                svg_poly_pattern = svg_maker.xml_create_pattern(
                    pattern_polygon_coordinates
                )
                svg_finalized_pattern = svg_str_pattern.replace(
                    svg_maker.poly_placeholder, svg_poly_pattern["string"]
                )

                # Save and print
                print(
                    f"\r > Saved pattern to [cyan]{svg_maker.save_svg(svg_finalized_pattern)}[/cyan] & [cyan]{svg_maker.save_png(svg_finalized_pattern)}[/cyan]"
                )

                return [
                    pattern_container,
                    pattern_polygon_container,
                    pattern_polygons_objects,
                    pattern_polygon_coordinates,
                ]


if __name__ == "__main__":
    cli_banner("Seigaiha")

    # Stop execution at keyboard input
    try:
        OUTPUT_DIRECTORY = "./output"
        PRESET_DIRECTORY = "./preset"

        svgs = main()
    except KeyboardInterrupt:
        print("\r\n\r\n> [red]Execution cancelled by user[/red]")
        sys.exit()
