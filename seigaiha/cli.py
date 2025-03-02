import click

from loguru import logger

import random
import math
from itertools import cycle
from shapely.geometry import Polygon, Point, LineString  # type: ignore[import-untyped]
from shapely import affinity  # type: ignore[import-untyped]
from seigaiha.args import (
    OutputPathChecker,
    OptionalValueChecker,
    InputPathChecker,
)
from seigaiha.helper import combine_arguments_by_batch
from seigaiha.svg import SVGmaker


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


def get_colours(polygon_collection: list, polygon_colours: list):
    """
    Get alternating colours for polygon filling.
    """

    polygon_count = len(polygon_collection)
    if len(polygon_colours) < polygon_count:
        colour_cycle = cycle(polygon_colours)
        colour_repeat_collection = []
        for _ in range(0, polygon_count):
            colour_repeat_collection.append(next(colour_cycle))

        return colour_repeat_collection

    return polygon_colours


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
    polygon_colours,
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

    # Get colours to fill
    polygon_colours = get_colours(polygon_collection, polygon_colours)

    return [boundary_box, polygon_collection, polygon_coordinates, polygon_colours]


@logger.catch
@click.command(
    context_settings={"help_option_names": ["-h", "--help"]},
    epilog="Repository: https://github.com/ToshY/seigaiha",
)
@click.option(
    "--input-path",
    "-i",
    type=click.Path(exists=True, dir_okay=True, file_okay=True, resolve_path=True),
    required=False,
    multiple=True,
    callback=InputPathChecker(),
    show_default=True,
    default=["./input"],
    help="Path to input file or directory with preset options",
)
@click.option(
    "--output-path",
    "-o",
    type=click.Path(dir_okay=True, file_okay=True, resolve_path=True),
    required=False,
    multiple=True,
    callback=OutputPathChecker(),
    show_default=True,
    default=["./output"],
    help="Path to output file or directory",
)
@click.option(
    "--extension",
    "-e",
    type=click.Choice(['["svg", "png"]', '["svg"]', '["png"]']),
    required=False,
    multiple=True,
    callback=OptionalValueChecker(),
    show_default=True,
    default=['["svg", "png"]'],
    help="Output file extension",
)
@click.option(
    "--unique-filename/--no-unique-filename",
    is_flag=True,
    show_default=True,
    default=True,
    help="Create files with unique filenames by using current datetime suffix",
)
def cli(
    input_path,
    output_path,
    extension,
    unique_filename,
):
    combined_result = combine_arguments_by_batch(input_path, output_path, extension)

    for item in combined_result:
        current_batch = item.get("batch")
        current_output_extension = item.get("extension")
        current_output = item.get("output").get("resolved")
        current_input_original_batch_name = item.get("input").get("given")
        current_input_files = item.get("input").get("resolved")
        total_current_input_files = len(current_input_files)

        for current_file_path_index, current_file_item in enumerate(
            current_input_files
        ):
            if current_file_path_index == 0:
                logger.info(
                    f"Seigaiha batch `{current_batch}` for `{current_input_original_batch_name}` started."
                )

            current_file_path = current_file_item.get("path")
            current_preset = current_file_item.get("content")

            seed = current_preset.get("seed", None)
            random.seed(seed)

            width = current_preset.get("output", {"resolution": 2500}).get("resolution")
            fractions = current_preset.get("fractions")
            edges = current_preset.get("edges", 36)
            spacing = current_preset.get("spacing", 0)
            rotation = current_preset.get("rotation", 0)
            pattern = current_preset.get("pattern", False)
            colours = current_preset.get("colours", [])

            # colours to tuple
            colours = [tuple(el.values()) for el in colours]

            # Create polygon object
            box_dimensions, polygon_objects, polygon_coordinates, colours_format = (
                create_polygon(edges, fractions, colours, width, spacing, rotation)
            )

            # Init SVGmaker
            svg_maker = SVGmaker(
                current_preset, [box_dimensions["width"], box_dimensions["height"]]
            )

            # Create single SVG string
            polygons_and_colours = [
                {
                    "polygon": polygon_coordinates,
                    "broken": False,
                    "colour": colours_format,
                }
            ]
            xml_result = svg_maker.xml_result(polygons_and_colours)

            for output_extension in current_output_extension:
                output_path = svg_maker.prepare_output_path(
                    current_file_path,
                    current_output,
                    output_extension,
                    unique_filename,
                )
                if output_extension == "svg":
                    svg_maker.save_svg(xml_result, output_path)

                if output_extension == "png":
                    svg_maker.save_png(xml_result, output_path)

                logger.info(f"Saved Seigaiha element to `{str(output_path)}`.")

            # %% pattern
            if pattern:
                svg_str_pattern = svg_maker.xml_initialise_pattern()
                svg_pattern = svg_maker.xml_setup_pattern()

                # "Broken" polygon should be a "normal" polygon if a broken pattern is not specified
                broken_polygon = polygon_objects[:fractions]

                broken_pattern = pattern.get("broken", False)
                if broken_pattern:
                    # Prepare broken polygon and colours
                    broken_colours_tuple = [
                        tuple(el.values())
                        for el in broken_pattern.get(
                            "colours", current_preset.get("colours", [])
                        )
                    ]

                    fractions = broken_pattern.get("fractions", fractions)
                    _, broken_polygon_objects, _, broken_colours_format = (
                        create_polygon(
                            edges,
                            fractions,
                            broken_colours_tuple,
                            width,
                            spacing,
                            rotation,
                        )
                    )

                    broken_polygon = broken_polygon_objects[:fractions]

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
                                "colour": (
                                    colours_format
                                    if not is_broken
                                    else broken_colours_format
                                ),
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
                for output_extension in current_output_extension:
                    output_path = svg_maker.prepare_output_path(
                        current_file_path,
                        current_output,
                        output_extension,
                        unique_filename,
                        "seigaiha",
                    )
                    if output_extension == "svg":
                        svg_maker.save_svg(svg_finalized_pattern, output_path)

                    if output_extension == "png":
                        svg_maker.save_png(svg_finalized_pattern, output_path)

                    logger.info(f"Saved Seigaiha pattern to `{str(output_path)}`.")

            if current_file_path_index != total_current_input_files - 1:
                continue

            logger.info(
                f"Seigaiha batch `{current_batch}` for `{current_input_original_batch_name}` finished."
            )
