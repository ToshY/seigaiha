# -*- coding: utf-8 -*-
"""
Created on Wed Jul 22 16:29:25 2020

@author: ToshY
"""

import datetime
import random
import numpy as np
from shapely import affinity
from cairosvg import svg2png
from functools import reduce


class SVGmaker:

    poly_placeholder = "%polygons%"

    def __init__(
        self, data, output_dir, dims, scale=1, vbox=[0, 0, -1, -1], constraint=182.25
    ):
        # Initial image dimensions
        self.width, self.height = dims

        # Scale to max resolution
        if scale == 1:
            self.scale = scale
        else:
            self.scale = scale / max(dims)

        # Check scale does not exceed 182.5 megapixels constraint
        mp = ((self.width * self.height) * self.scale ** 2) / 1e6
        if mp >= constraint:
            # Solve what scale should be for 182 MP
            self.scale = ((round(constraint) * 1e6) / (self.width * self.height)) ** (
                1 / 2
            )

        # Viewbox
        self.view_box = self._check_viewbox(vbox)
        if self.view_box[-2:] == [-1, -1]:
            self.view_box[-2:] = dims

        # Scale
        if self.scale != 1:
            self.view_box = [self.scale * x for x in self.view_box]
            self.width, self.height = self.view_box[-2:]

        # Center polygon
        self.xcenter = self.width / 2
        self.ycenter = self.height / 2

        # Output
        self.output_file_name = self._file_naming(data, output_dir)

    def xml_init(self, shape_rendering="geometricprecision"):
        """
        Initialize XML

        Returns
        -------
        xml_str : TYPE
            DESCRIPTION.

        """

        xml_str = '<?xml version="1.0" encoding="UTF-8"?>\r\n'
        xml_str += '<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">\r\n'
        xml_str += '<svg version="1.1" id="" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" preserveAspectRatio="xMidYMid meet" '
        xml_str += (
            'width="' + str(self.width) + 'px" height="' + str(self.height) + 'px" '
        )
        xml_str += 'viewBox="' + self.join_list(self.view_box) + '">\r\n'
        xml_str += (
            '<g style="shape-rendering:geometricprecision' + shape_rendering + ';">\r\n'
        )
        xml_str += self.poly_placeholder
        xml_str += "</g>\r\n"
        xml_str += "</svg>"

        return xml_str

    def xml_poly(self, polygon, colours):
        """ Create polygon segments """

        # Loop over points and format to svg polygon
        xml_poly = ""
        for idx, (s, c) in enumerate(zip(polygon, colours)):
            tmpx = ""
            for p in s:
                tmpx = " ".join([tmpx, ",".join(str(e * self.scale) for e in p)])

            # Strip leading whitespace
            tmpx = tmpx.strip()

            # Get HEX colours
            chex = self.rgb2hex(c[3], c[2], c[1])

            # Append poly path
            xml_poly += (
                '<path d="M'
                + tmpx
                + 'z" fill="'
                + chex
                + '" fill-opacity="'
                + str(c[0])
                + '"/>'
            )

        return xml_poly

    def xml_setup_pattern(self, pattern_info):
        hz = pattern_info["horizontal"]
        vt = pattern_info["vertical"]
        br = pattern_info["broken"]

        # Standard pattern
        xl = np.linspace(
            0, round(self.width * hz["spacing"] * hz["amount"]), hz["amount"] + 1
        ).tolist()[:-1]
        yl = np.linspace(
            0, round(self.height * vt["spacing"] * vt["amount"]), vt["amount"] + 1
        ).tolist()[:-1]

        pattern_list = [[] for el in yl]
        for iy in range(len(yl)):
            ix_list = []
            for ix in range(len(xl)):
                ix_list.append((self.xcenter + xl[ix], self.ycenter + yl[iy]))

            pattern_list[iy].append(ix_list)

        pattern_list = reduce(lambda x, y: x + y, pattern_list)

        # Broken Total Factor in pattern
        btf = round(br * (hz["amount"] * vt["amount"]))

        # Somewhat equally distributed random items to break in pattern per line
        broken_polygons = [
            round(sum(x) / 2)
            for x in zip(
                self._random_partition(btf, vt["amount"]),
                self._random_partition(btf, vt["amount"]),
            )
        ]

        # Check if some are broken
        if sum(broken_polygons) > 0:
            for x, k in enumerate(pattern_list):
                broken_hz = broken_polygons[x]
                bk = 0
                while bk < broken_hz:
                    pattern_list[x][self._random_index(pattern_list[x])] = (None, None)
                    bk += 1

        # Pattern list to fill polygons with
        return pattern_list

    def xml_create_pattern(self, polygons, colours):
        xml_pattern = []
        for p in polygons:
            xml_pattern.append(self.xml_poly(p, colours))
        return {"paths": xml_pattern, "string": "\r\n".join(xml_pattern)}

    def xml_repeat_pattern(self, polygon, colours):
        """

        Create XML repeating pattern

        Parameters
        ----------
        polygon : TYPE
            DESCRIPTION.
        colours : TYPE
            DESCRIPTION.

        Returns
        -------
        xml_str : TYPE
            DESCRIPTION.

        """

        xml_str = '<?xml version="1.0" encoding="UTF-8"?>\r\n'
        xml_str += '<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">\r\n'
        xml_str += '<svg version="1.1" id="" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" preserveAspectRatio="xMidYMid meet" '
        xml_str += 'width="100%" height="100%" '
        xml_str += 'viewBox="' + self.join_list(self.view_box) + '">\r\n'
        xml_str += "<defs>\r\n"
        xml_str += '<pattern id="puzzle" x="0" y="0" width="56" height="28" patternUnits="userSpaceOnUse">\r\n'
        xml_str += (
            '<path fill="#66cc99" stroke="#555555" stroke-width="2.0" opacity="0.6" '
        )
        xml_str += 'd="M56 26v2h-7.75c2.3-1.27 4.94-2 7.75-2zm-26 2a2 2 0 1 0-4 0h-4.09A25.98 25.98 0 0 0 0 16v-2c.67 0 1.34.02 2 .07V14a2 2 0 0 0-2-2v-2a4 4 0 0 1 3.98 3.6 28.09 28.09 0 0 1 2.8-3.86A8 8 0 0 0 0 6V4a9.99 9.99 0 0 1 8.17 4.23c.94-.95 1.96-1.83 3.03-2.63A13.98 13.98 0 0 0 0 0h7.75c2 1.1 3.73 2.63 5.1 4.45 1.12-.72 2.3-1.37 3.53-1.93A20.1 20.1 0 0 0 14.28 0h2.7c.45.56.88 1.14 1.29 1.74 1.3-.48 2.63-.87 4-1.15-.11-.2-.23-.4-.36-.59H26v.07a28.4 28.4 0 0 1 4 0V0h4.09l-.37.59c1.38.28 2.72.67 4.01 1.15.4-.6.84-1.18 1.3-1.74h2.69a20.1 20.1 0 0 0-2.1 2.52c1.23.56 2.41 1.2 3.54 1.93A16.08 16.08 0 0 1 48.25 0H56c-4.58 0-8.65 2.2-11.2 5.6 1.07.8 2.09 1.68 3.03 2.63A9.99 9.99 0 0 1 56 4v2a8 8 0 0 0-6.77 3.74c1.03 1.2 1.97 2.5 2.79 3.86A4 4 0 0 1 56 10v2a2 2 0 0 0-2 2.07 28.4 28.4 0 0 1 2-.07v2c-9.2 0-17.3 4.78-21.91 12H30zM7.75 28H0v-2c2.81 0 5.46.73 7.75 2zM56 20v2c-5.6 0-10.65 2.3-14.28 6h-2.7c4.04-4.89 10.15-8 16.98-8zm-39.03 8h-2.69C10.65 24.3 5.6 22 0 22v-2c6.83 0 12.94 3.11 16.97 8zm15.01-.4a28.09 28.09 0 0 1 2.8-3.86 8 8 0 0 0-13.55 0c1.03 1.2 1.97 2.5 2.79 3.86a4 4 0 0 1 7.96 0zm14.29-11.86c1.3-.48 2.63-.87 4-1.15a25.99 25.99 0 0 0-44.55 0c1.38.28 2.72.67 4.01 1.15a21.98 21.98 0 0 1 36.54 0zm-5.43 2.71c1.13-.72 2.3-1.37 3.54-1.93a19.98 19.98 0 0 0-32.76 0c1.23.56 2.41 1.2 3.54 1.93a15.98 15.98 0 0 1 25.68 0zm-4.67 3.78c.94-.95 1.96-1.83 3.03-2.63a13.98 13.98 0 0 0-22.4 0c1.07.8 2.09 1.68 3.03 2.63a9.99 9.99 0 0 1 16.34 0z">'
        xml_str += "</path>\r\n"
        xml_str += "</pattern>\r\n"
        xml_str += "</defs>\r\n"
        xml_str += (
            '<rect fill="url(#Pattern)" x="0" y="0" width="100%" height="100%" />\r\n'
        )
        xml_str += "</svg>"

        return xml_str

    def save_svg(self, content):
        """ Write string to file """

        ctime = datetime.datetime.now().strftime("%d-%m-%Y_%H-%M-%S-%f")
        svg_file = self.output_file_name + f"_{ctime}" + ".svg"
        text_file = open(svg_file, "wt")
        text_file.write(content)
        text_file.close()

        return svg_file

    def save_png(self, content):
        """ Save SVG as PNG """

        ctime = datetime.datetime.now().strftime("%d-%m-%Y_%H-%M-%S-%f")
        png_file = self.output_file_name + f"_{ctime}" + ".png"
        svg2png(bytestring=content, write_to=png_file)

        return png_file

    def join_list(self, x, deli=" "):
        """ Join lists/tuples to string """

        return deli.join(map(str, x))

    def rgb2hex(self, r, g, b):
        """ RGB to Hexadecimal """

        return "#{0:02x}{1:02x}{2:02x}".format(
            self._rgbounds(r), self._rgbounds(g), self._rgbounds(b)
        )

    def _file_naming(self, data, output_dir):
        """ File naming """

        # Output split
        output_path = list(output_dir.keys())[0]
        output_type = list(output_dir.values())[0]

        # Prepare output file name
        if output_type == "directory":
            return str(
                output_path.joinpath(
                    "_".join(
                        [
                            "{}-{}".format(k, v)
                            for k, v in data.items()
                            if k not in ["repeat", "colours"]
                        ]
                    )
                )
            )

        return str(output_path.with_suffix(""))

    def _rgbounds(self, x):
        """ RGB boundaries """

        return max(0, min(x, 255))

    def _check_viewbox(self, c):
        """ Check viewbox numerical values """

        vb = [s for s in c if isinstance(s, (int, float))]
        if len(vb) != len(c):
            raise Exception(
                "Invalid viewbox specified. Please make sure that the viewbox only contains numerical values."
            )
        else:
            return vb

    def _random_partition(self, n, s):
        partition = [0] * s
        for x in range(n):
            partition[random.randrange(s)] += 1
        return partition

    def _random_index(self, n):
        return random.randrange(len(n))

    def _linspace(self, d, u, l):
        return [d + x * (u - d) / l for x in range(l)]
