# -*- coding: utf-8 -*-
"""
Created on Mon Oct 19 22:30:50 2020

@author: ToshY

Seigaiha SVG pattern maker
"""

import argparse
import numpy as np
import math
from pathlib import Path
from src.banner import cli_banner
from src.args import FileDirectoryCheck, files_in_dir
from shapely.geometry import Polygon, MultiPolygon, Point
from shapely import affinity
from shapely.ops import unary_union
from src.svg import SVGmaker
from src.general import (
    read_json,
    remove_empty_dict_values,
    dict_to_list,
    split_list_of_dicts_by_key,
)
from itertools import cycle
from rich import print
import matplotlib.pyplot as plt


def cli_args():
    """
    Command Line argument parser.

    Returns
    -------
    list
        List of dictonaries of seigaiha presets.

    """

    # Arguments
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "-p",
        "--preset",
        type=str,
        required=True,
        action=FileDirectoryCheck,
        const=False,
        nargs="+",
        help="Path to JSON file or directory with preset options",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        required=True,
        action=FileDirectoryCheck,
        const=False,
        nargs="+",
        help="Path to output file or directory",
    )
    args = parser.parse_args()

    # Check args count
    user_args = check_args(args.preset, args.output)

    return user_args


def check_args(presets, outputs):
    """
    Check the amount of input arguments, outputs and presets.

    Parameters
    ----------
    presets : list
        Input preset argument(s).
    outputs : list
        Output arugment(s)

    Returns
    -------
    None.

    """

    len_presets = len(presets)
    len_outputs = len(outputs)

    if len_presets != len_outputs:
        if len_outputs != 1:
            raise Exception(
                f"[red]Amount of preset arguments ({len_presets}) "
                "does not equal the amount of output arguments ({len_outputs})."
            )

    # Prepare inputs/outputs/presets
    batch = {}
    for i, el in enumerate(presets):

        cpath = [*el][0]
        ptype = el[cpath]

        if ptype == "file":
            all_files = [Path(cpath)]
            data = read_json(cpath)
        elif ptype == "directory":
            all_files = files_in_dir(cpath)
            data = [read_json(fl) for fl in all_files]

        len_all_files_in_batch = len(all_files)

        if len_outputs == 1:
            output_files = [[*outputs][0]]
            output_type = str(*outputs[0].values())
            if ptype == "directory":
                if len_all_files_in_batch > len_outputs and output_type == "file":
                    raise Exception(
                        f"The path `{str(cpath)}` contains"
                        f" `{len_all_files_in_batch}` files but only"
                        f" `{len_outputs}`"
                        f" output filename(s) was/were specified."
                    )
                else:
                    output_files = [outputs[0] for x in range(len(all_files))]
        else:
            output_files = outputs[0]
            # Unset
            outputs.pop(0)
            # Check type
            if ptype == "directory":
                # Create copies
                output_files = [output_files for x in range(len(all_files))]

        batch[str(i)] = {
            "input": all_files,
            "data": data,
            "output": output_files,
        }

    return batch


def get_polygon_points(numSides, x, y, side_length):
    """
    Polygon points

    Parameters
    ----------
    numSides : TYPE
        DESCRIPTION.
    x : TYPE
        DESCRIPTION.
    y : TYPE
        DESCRIPTION.
    side_length : TYPE
        DESCRIPTION.

    Returns
    -------
    pts : TYPE
        DESCRIPTION.

    """
    pts = []
    for i in range(numSides):
        x = x + side_length * math.cos(math.pi * 2 * i / numSides)
        y = y + side_length * math.sin(math.pi * 2 * i / numSides)
        pts.append((x, y))

    return pts


def get_polygon_object(points):
    """ Get a polygon object from given points """

    if len(np.array(points).shape) > 2:
        return [Polygon(p) for p in zip(*points)]

    return Polygon([[p[0], p[1]] for p in points])


def get_polygon_coords(polygons):
    """ Get coordinates from given polygon(s) (without loop) """

    if type(polygons) is list:
        return [list(v.exterior.coords)[:-1] for v in polygons]

    return list(polygons.exterior.coords)[:-1]


def get_colours(polygon_list, polygon_colours):
    """ Get alternating colours for polygon filling """

    bgr = reverse_colours(polygon_colours)

    if len(bgr) < len(polygon_list):
        colours_cycle = cycle(bgr)
        nlb = []
        for i in range(0, len(polygon_list)):
            nlb.append(next(colours_cycle))

        return nlb

    return bgr


def reverse_colours(colours: list):
    """ Reverse colours in list of tuples """

    return [c[::-1] for c in colours]


def create_polygon(
    poly_edges, poly_fractions, poly_colours, poly_width, spacing=0.5, poly_rotation=0
):
    """ Create a single polygon """

    # Polygon image width
    pw = poly_width / 2

    # Get polygon points
    all_points = get_polygon_points(poly_edges, pw, pw, pw)

    # Get polygon object
    polyg = get_polygon_object(all_points)

    # Retreive polygon boundary box coordinates
    x1, y1, x2, y2 = polyg.bounds
    box_dims = {
        "width": max([x1, x2]) - min([x1, x2]),
        "height": max([y1, y2]) - min([y1, y2]),
    }

    # Rotate
    if poly_rotation != 0:
        polyg = affinity.rotate(polyg, poly_rotation, origin="centroid")
        x1, y1, x2, y2 = polyg.bounds
        box_dims = {
            "width": max([x1, x2]) - min([x1, x2]),
            "height": max([y1, y2]) - min([y1, y2]),
        }

    # Translate
    polyg = affinity.translate(polyg, -x1, -y1)

    # Get center coordinates of polygon
    px_center = polyg.centroid.x
    py_center = polyg.centroid.y

    # Get new coordinates for all points
    all_points = get_polygon_coords(polyg)

    # Fractions list
    if spacing is not None:
        frcs = []
        for i, v in enumerate(list(range(1, poly_fractions + 1))):
            if (i % 2) != 0:
                frcs.append((v / poly_fractions))
            else:
                vl = (v / poly_fractions) - (spacing) * 1 / poly_fractions
                frcs.append(vl if vl <= 1 else 1)
    else:
        frcs = [v / poly_fractions for v in list(range(1, poly_fractions + 1))]

    # Create all (sub)polygons
    vct = []
    for el in all_points:
        pxl = [
            ((px_center - el[0]) * x + el[0], (py_center - el[1]) * x + el[1])
            for x in frcs
        ]
        vct.append([el] + pxl)

    # The polygons are created
    plgns = [Polygon(elk) for elk in zip(*vct)]

    # If even, remove the last unnessesary entry (0 pixels)
    if poly_fractions % 2 == 0:
        plgns = plgns[:-1]

    # Get coords back
    plgnsc = get_polygon_coords(plgns)

    # Get colours to fill
    clrs = get_colours(plgns, poly_colours)

    return [box_dims, plgns, plgnsc, clrs]


def main():
    # Input arguments
    presets = cli_args()

    # Iterate over presets
    for x, b in presets.items():
        for y, fl in enumerate(b["input"]):
            # Check if first/last item for reporting
            output = b["output"][y]
            data = b["data"]
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
            box_dims, polygon_objs, polygon_coords, colours_format = create_polygon(
                edges, fractions, colours, width, spacing, rotation
            )

            # Init SVGmaker
            SVG = SVGmaker(data, output, [box_dims["width"], box_dims["height"]])

            # Create single SVG string
            svg_str = SVG.xml_init()
            svg_poly = SVG.xml_poly([polygon_coords], colours_format)
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
                        "Not all necessary keys `factor`, `fractions` and `colours` for broken pattern are specified."
                    )

                if broken_pattern["fractions"] >= fractions:
                    raise Exception(
                        "The `fractions` key for broken pattern can not be equal or larger than the main `fractions` key."
                    )

                if len(broken_pattern["colours"]) != broken_pattern["fractions"]:
                    raise Exception(
                        "The amount of colours for the broken pattern has to be the same as specified broken `fractions`."
                    )

                # Colours to tuple
                broken_colours = reverse_colours(
                    [tuple(el.values()) for el in broken_pattern["colours"]]
                )

                # Create pattern setup
                svg_pattern = SVG.xml_setup_pattern(data["repeat"])

                # Create copies of the initial "single" polygon and translate conform pattern
                pattern_polygons_objects = []
                for idx, row in enumerate(svg_pattern):
                    pattern_polygons_objects.append([])
                    polygons_row_objects = []
                    for ix, xl in enumerate(row):
                        xp = xl[0]
                        yp = xl[1]
                        broken = xl[2]["broken"]
                        if broken is True:
                            single_polygon = polygon_objs[: broken_pattern["fractions"]]
                        else:
                            single_polygon = polygon_objs

                        transformed_polygon = [
                            affinity.translate(p, xp, yp) for p in single_polygon
                        ]

                        polygons_row_objects.append(
                            {"polygon": transformed_polygon, "broken": broken}
                        )

                    pattern_polygons_objects[idx] = polygons_row_objects

                # plt.plot(*pattern_polygons_objects[0][0]['polygon'][0].exterior.coords.xy)
                # plt.show()

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
                        last_polygon_bounds[3] - (polygon_height / 2),
                    ),
                    (
                        last_polygon_bounds[2] - (polygon_width / 2),
                        last_polygon_bounds[3] - (polygon_height / 2),
                    ),
                    (
                        last_polygon_bounds[2] - (polygon_width / 2),
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
                                # plt.plot(*pattern_polygons_objects[idx][idy]['polygon'][idp].exterior.coords.xy)

                        single_polygon_coords_new = get_polygon_coords(
                            pattern_polygons_objects_copy[idx][idy]["polygon"]
                        )
                        polygons_row_new.append(
                            {
                                "polygon": single_polygon_coords_new,
                                "broken": pattern_polygons_objects[idx][idy]["broken"],
                            }
                        )

                    pattern_polygon_coordinates[idx] = polygons_row_new

                # plt.show()
                # return [colours_format, polygon_objs, pattern_polygons_objects, pattern_polygon_coordinates]

                # Create the actual pattern;
                svg_poly_pattern = SVG.xml_create_pattern(
                    pattern_polygon_coordinates, colours_format, broken_colours
                )
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


if __name__ == "__main__":
    """ Main """
    cli_banner(__file__, banner_font="slant")

    # Stop execution at keyboard input
    try:
        svgs = main()
    except KeyboardInterrupt:
        print("\r\n\r\n> [red]Execution cancelled by user[/red]")
        exit()
