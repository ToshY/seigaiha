# -*- coding: utf-8 -*-
"""
Created on Mon Oct 19 22:30:50 2020

@author: ToshY

Seigaiha SVG pattern maker
"""

import numpy as np
import math
import matplotlib.pyplot as plt
from pathlib import Path
from shapely.geometry import Polygon
from shapely import affinity
from shapely.ops import cascaded_union
from src.createSVG import SVGmaker
from src.general import General
from itertools import cycle


def get_polygon_points(numSides, x, y, side_length):
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

    bgr = [t[::-1] for t in polygon_colours]

    if len(bgr) < len(polygon_list):
        colours_cycle = cycle(bgr)
        nlb = []
        for i in range(0, len(polygon_list)):
            nlb.append(next(colours_cycle))

        return nlb

    return bgr


def create_polygon(
    poly_edges, poly_recursive, poly_colours, poly_width, spacing=True, poly_rotation=0
):
    """ Create a single polygon """

    # Polygon image width
    pw = poly_width / 2

    # Get polygon points
    all_points = get_polygon_points(edges, pw, pw, pw)

    # Get polygon object
    polyg = get_polygon_object(all_points)

    # Retreive polygon boundary box coordinates
    x1, y1, x2, y2 = polyg.bounds
    box_dims = {
        "width": max([x1, x2]) - min([x1, x2]),
        "height": max([y1, y2]) - min([y1, y2]),
    }

    # Rotate
    if rot != 0:
        polyg = affinity.rotate(polyg, rot, origin="centroid")
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
        for i, v in enumerate(list(range(1, fractions + 1))):
            if (i % 2) != 0:
                frcs.append((v / fractions))
            else:
                vl = (v / fractions) - (spacing) * 1 / fractions
                frcs.append(vl if vl <= 1 else 1)
    else:
        frcs = [v / fractions for v in list(range(1, fractions + 1))]

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
    if poly_recursive % 2 == 0:
        plgns = plgns[:-1]

    # Get coords back
    plgnsc = get_polygon_coords(plgns)

    # Get colours to fill
    clrs = get_colours(plgns, colours)

    return [box_dims, plgns, plgnsc, clrs]


def save_output(width, height, points, colours, scale, svg=True, png=True):
    """ Save output SVG and PNG """

    SVG = SVGmaker([width, height], scale)
    # Create SVG string
    svg_str = SVG.xml_init()
    svg_poly = SVG.xml_poly(points, colours)
    svg_final = svg_str.replace(SVG.poly_placeholder, svg_poly)

    # Save SVG/PNG
    fnl = []
    if svg:
        fnl.append(GNR.save_svg(svg_final, ".svg"))
    if png:
        fnl.append(GNR.save_png(svg_final, ".png"))

    return " & ".join(fnl)


def cwd():
    """ Get current working directory """

    return Path(__file__).cwd()


if __name__ == "__main__":
    """ Main """
    start_dims = 1000
    fractions = 7
    edges = 9
    colours = [(0, 0, 0), (255, 255, 255)]
    repeat = [6, 10]
    rot = 0
    spacing = 1 / 2

    # Create polygon object
    box_dims, polygon_objs, polygon_coords, colours = create_polygon(
        edges, fractions, colours, start_dims, spacing, rot
    )

    # CWD
    wdir = cwd()

    # Prepare file
    fname = "C-" + str(edges)
    GNR = General(str(wdir), fname)

    # Create file
    # print(polygon_coords)
    sout = save_output(
        box_dims["width"], box_dims["height"], polygon_coords, colours, start_dims
    )
