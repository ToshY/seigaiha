# -*- coding: utf-8 -*-

import datetime
import random
import numpy as np
from cairosvg import svg2png


def _get_formatted_datetime():
    """Get formatted datetime"""

    return datetime.datetime.now().strftime("%d-%m-%Y_%H-%M-%S-%f")


class SVGmaker:
    poly_placeholder = "%polygons%"

    svg_desc = "Rendered with Seigaiha | https://github.com/ToshY/seigaiha"

    def __init__(
        self,
        data,
        output_directory,
        dims,
        scale=1,
        vbox=[0, 0, -1, -1],
        constraint=182.25,
    ):
        # Initial image dimensions
        self.width, self.height = dims

        # Scale to max resolution
        if scale == 1:
            self.scale = scale
        else:
            self.scale = scale / max(dims)

        # Check scale does not exceed constraint
        mp = ((self.width * self.height) * self.scale**2) / 1e6
        if mp >= constraint:
            # Solve what scale should be for constraint
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

        # Spacing and factor
        self.xnodes = data["repeat"]["horizontal"]["amount"]
        self.xspacing_factor = data["repeat"]["horizontal"]["spacing"]
        self.ynodes = data["repeat"]["vertical"]["amount"]
        self.yspacing_factor = data["repeat"]["vertical"]["spacing"]

        # Pattern single polygon calculated dimensions
        self.calculated_single_polygon_width_for_pattern = self.width / (
            data["repeat"]["horizontal"]["amount"] - 1
        )
        self.pattern_width = self.width * self.xspacing_factor
        self.calculated_single_polygon_height_for_pattern = (
            self.height / self.width
        ) * self.calculated_single_polygon_width_for_pattern
        self.pattern_height = data["repeat"]["vertical"][
            "amount"
        ] * self.yspacing_factor * self.calculated_single_polygon_height_for_pattern - (
            self.calculated_single_polygon_height_for_pattern / 2
        )

        # Output
        self.output_directory = str(output_directory)
        self.output_file_name = self._file_naming(data)

    def xml_init(self, shape_rendering="geometricprecision"):
        """
        Initialize XML

        Returns
        -------
        xml_str : TYPE
            DESCRIPTION.

        """

        xml_str = '<?xml version="1.0" encoding="UTF-8"?>\r\n'
        xml_str += (
            '<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" '
            '"http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">\r\n'
        )
        xml_str += (
            '<svg version="1.1" xmlns="http://www.w3.org/2000/svg" '
            'xmlns:xlink="http://www.w3.org/1999/xlink" preserveAspectRatio="xMidYMid meet" '
        )
        xml_str += (
            'width="' + str(self.width) + 'px" height="' + str(self.height) + 'px" '
        )
        xml_str += 'viewBox="' + self.join_list(self.view_box) + '">\r\n'
        xml_str += '<g style="shape-rendering:' + shape_rendering + ';">\r\n'
        xml_str += self.poly_placeholder
        xml_str += "</g>\r\n"
        xml_str += "<desc>" + self.svg_desc + "</desc>"
        xml_str += "</svg>"

        return xml_str

    def xml_init_pattern(self, shape_rendering="geometricprecision"):
        """
        Initialize XML

        Returns
        -------
        xml_str : TYPE
            DESCRIPTION.

        """

        view_box = self.view_box
        view_box[0] = view_box[0] + self.width
        view_box[1] = view_box[1] + self.height
        view_box[2] = view_box[2] * self.xnodes - self.width
        view_box[3] = view_box[3] / self.ynodes

        xml_str = '<?xml version="1.0" encoding="UTF-8"?>\r\n'
        xml_str += (
            '<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" '
            '"http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">\r\n'
        )
        xml_str += (
            '<svg version="1.1" id="" xmlns="http://www.w3.org/2000/svg" '
            'preserveAspectRatio="xMinYMin" '
        )

        xml_str += (
            'width="'
            + str(self.pattern_width)
            + 'px" '
            + 'height="'
            + str(self.pattern_height)
            + 'px" '
        )
        xml_str += 'viewBox="' + self.join_list(view_box) + '">\r\n'
        xml_str += '<g style="shape-rendering:' + shape_rendering + ';">\r\n'
        xml_str += self.poly_placeholder
        xml_str += "</g>\r\n"
        xml_str += "<desc>" + self.svg_desc + "</desc>"
        xml_str += "</svg>"

        return xml_str

    def xml_poly(self, polygon: list):
        """Create polygon segments"""

        xml_final = ""
        for idx, part in enumerate(polygon):
            xml_poly = "<g>"
            poly = part["polygon"]
            colours = part["colour"]

            for ip, poly_slice in enumerate(poly):
                hex_colour = self.rgb2hex(
                    colours[ip][0], colours[ip][1], colours[ip][2]
                )
                xml_poly += (
                    '<path d="M'
                    + " ".join("%s,%s" % tup for tup in poly_slice)
                    + 'Z" fill="'
                    + hex_colour
                    + '" fill-opacity="'
                    + str(colours[ip][3])
                    + '"/>'
                )
            xml_poly += "</g>"
            xml_final += xml_poly

        return xml_final

    def xml_setup_pattern(self, pattern_info):
        horizontal = pattern_info["horizontal"]
        vertical = pattern_info["vertical"]
        broken = pattern_info["broken"]
        alternate = pattern_info["alternate"]

        # Standard pattern
        xl = np.linspace(
            0,
            round(self.width * horizontal["spacing"] * horizontal["amount"]),
            horizontal["amount"] + 1,
        ).tolist()[:-1]

        xli = xl
        if alternate >= 0:
            xli = [(v + self.xcenter) * alternate for v in xl]

        yl = np.linspace(
            0,
            round(self.height * vertical["spacing"] * vertical["amount"]),
            vertical["amount"] + 1,
        ).tolist()[:-1]

        pattern_list = [[] for _ in yl]
        for iy in range(len(yl)):
            ix_list = []
            xll = xl
            if iy % 2 != 0:
                xll = xli
            for ix in range(len(xll)):
                ix_list.append(
                    (self.xcenter + xll[ix], self.ycenter + yl[iy], {"broken": False})
                )

            pattern_list[iy] = ix_list

        # Broken Total Factor in pattern
        if not broken["factor"] and broken["factor"] < 0:
            raise Exception("The broken factor was not specified.")
        broken_total_factor = round(
            broken["factor"] * (horizontal["amount"] * vertical["amount"])
        )

        # Somewhat equally distributed random items to break in pattern per line
        broken_polygons = [
            round(sum(x) / 2)
            for x in zip(
                self._random_partition(broken_total_factor, vertical["amount"]),
                self._random_partition(broken_total_factor, vertical["amount"]),
            )
        ]

        # Check if some are broken
        if sum(broken_polygons) > 0:
            for x, k in enumerate(pattern_list):
                broken_hz = broken_polygons[x]
                bk = 0
                while bk < broken_hz:
                    pattern_list[x][self._random_index(pattern_list[x])][-1][
                        "broken"
                    ] = True
                    bk += 1

        # Pattern list to fill polygons with
        return pattern_list

    def xml_create_pattern(self, polygons: list):
        xml_pattern = []
        for p in polygons:
            xml_pattern.append(self.xml_poly(p))

        return {"paths": xml_pattern, "string": "\r\n".join(xml_pattern)}

    def save_svg(self, content):
        """Write string to file"""

        svg_file = f"{self.output_directory}/{_get_formatted_datetime()}_{self.output_file_name}.svg"
        text_file = open(svg_file, "wt")
        text_file.write(content)
        text_file.close()

        return svg_file

    def save_png(self, content):
        """Save SVG as PNG"""

        png_file = f"{self.output_directory}/{_get_formatted_datetime()}_{self.output_file_name}.png"
        svg2png(bytestring=content, write_to=png_file)

        return png_file

    # noinspection PyMethodMayBeStatic
    def join_list(self, x, deli=" "):
        """Join lists/tuples to string"""

        return deli.join(map(str, x))

    def rgb2hex(self, r, g, b):
        """RGB to Hexadecimal"""

        return "#{0:02x}{1:02x}{2:02x}".format(
            self._rgbounds(r), self._rgbounds(g), self._rgbounds(b)
        )

    # noinspection PyMethodMayBeStatic
    def _file_naming(self, data):
        """File naming based on preset options"""

        return "_".join(
            [
                "{}-{}".format(k, v)
                for k, v in data.items()
                if k not in ["repeat", "colours"]
            ]
        )

    # noinspection PyMethodMayBeStatic
    def _rgbounds(self, x):
        """RGB boundaries"""

        return max(0, min(x, 255))

    # noinspection PyMethodMayBeStatic
    def _check_viewbox(self, c):
        """Check viewbox numerical values"""

        vb = [s for s in c if isinstance(s, (int, float))]
        if len(vb) != len(c):
            raise Exception(
                "Invalid viewbox specified. Please make sure that the viewbox only contains "
                "numerical values."
            )
        else:
            return vb

    # noinspection PyMethodMayBeStatic
    def _random_partition(self, n, s):
        partition = [0] * s
        for x in range(n):
            partition[random.randrange(s)] += 1
        return partition

    # noinspection PyMethodMayBeStatic
    def _random_index(self, n):
        return random.randrange(len(n))
