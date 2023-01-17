# -*- coding: utf-8 -*-

import re
import base64
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

        # Center polygon
        self.single_polygon_x_center = self.width / 2
        self.single_polygon_y_center = self.height / 2

        # Scale to max resolution
        self.scale = scale
        if scale != 1:
            self.scale = scale / max(dims)

        # Check scale does not exceed constraint and solve if needed
        mega_pixel_constraint = ((self.width * self.height) * self.scale**2) / 1e6
        if mega_pixel_constraint >= constraint:
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

        if data["repeat"]:
            # Alternate
            self.repeat_alternate = data["repeat"]["alternate"]

            # Amount and spacing
            self.repeat_horizontal = data["repeat"]["horizontal"]
            self.repeat_horizontal_amount = self.repeat_horizontal["amount"]
            self.repeat_horizontal_spacing = self.repeat_horizontal["spacing"]
            self.repeat_vertical = data["repeat"]["vertical"]
            self.repeat_vertical_amount = self.repeat_vertical["amount"]
            self.repeat_vertical_spacing = self.repeat_vertical["spacing"]

            self.repeat_broken = data["repeat"]["broken"]

            # Skip edges so they do not contain any broken elements
            self.repeat_broken_skip_edge = self.repeat_broken["skip_edge"]

            # Image placeholder
            self.repeat_broken_images = self.repeat_broken["images"]
            if self.repeat_broken_images:
                for broken_image_index, broken_image in enumerate(
                    self.repeat_broken_images
                ):
                    b64_decoded_broken_image = base64.b64decode(broken_image).decode(
                        "utf-8"
                    )

                    decoded_image_determined_dict = (
                        self._determine_external_svg_dimensions(
                            b64_decoded_broken_image
                        )
                    )

                    b64_decoded_broken_image = decoded_image_determined_dict["svg"]

                    extracted_svg_part = self._extract_svg_part(
                        b64_decoded_broken_image
                    )

                    transform_width = (
                        self.width / decoded_image_determined_dict["width"]
                    )
                    transform_height = (
                        self.width / decoded_image_determined_dict["height"]
                    )

                    self.repeat_broken_images[broken_image_index] = (
                        f'<g transform="matrix({transform_width},0,0,{transform_height},%posX%,'
                        f'%posY%)">{extracted_svg_part}</g>'
                    )

            self.is_broken = False
            self.broken_factor = 0
            if self.repeat_broken["factor"] and self.repeat_broken["factor"] > 0:
                self.is_broken = True
                self.broken_factor = round(
                    self.repeat_broken["factor"]
                    * (self.repeat_horizontal_amount * self.repeat_vertical_amount)
                )

            # Pattern single polygon calculated dimensions
            self.calculated_single_polygon_width_for_pattern = self.width / (
                self.repeat_horizontal_amount - 1
            )
            self.pattern_width = self.width * self.repeat_horizontal_spacing
            self.calculated_single_polygon_height_for_pattern = (
                self.height / self.width
            ) * self.calculated_single_polygon_width_for_pattern
            self.pattern_height = (
                self.repeat_vertical_amount
                * self.repeat_vertical_spacing
                * self.calculated_single_polygon_height_for_pattern
                - (self.calculated_single_polygon_height_for_pattern / 2)
            )

            self.pattern_scale_factor = (
                self.calculated_single_polygon_width_for_pattern / self.width
            )

        # Output
        self.output_directory = str(output_directory)
        self.output_file_name = self._file_naming(data)

    def xml_init(self, shape_rendering: str = "geometricprecision") -> str:
        """

        Parameters
        ----------
        shape_rendering

        Returns
        -------
        str

        """
        xml_str = '<?xml version="1.0" encoding="UTF-8"?>\r\n'
        xml_str += (
            '<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" '
            '"http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">\r\n'
        )
        xml_str += (
            '<svg version="1.1" xmlns="http://www.w3.org/2000/svg" '
            'preserveAspectRatio="xMidYMid meet" '
        )
        xml_str += (
            'width="' + str(self.width) + 'px" height="' + str(self.height) + 'px" '
        )
        xml_str += 'viewBox="' + self.join_list(self.view_box) + '">\r\n'
        xml_str += '<g style="shape-rendering: ' + shape_rendering + ';">\r\n'
        xml_str += self.poly_placeholder
        xml_str += "</g>\r\n"
        xml_str += "<desc>" + self.svg_desc + "</desc>"
        xml_str += "</svg>"

        return xml_str

    def xml_init_pattern(self, shape_rendering: str = "geometricprecision") -> str:
        view_box = self.view_box
        view_box[0] = view_box[0] + self.width
        view_box[1] = view_box[1] + self.height
        view_box[2] = view_box[2] * self.repeat_horizontal_amount - self.width
        view_box[3] = view_box[3] / self.repeat_vertical_amount

        xml_str = '<?xml version="1.0" encoding="UTF-8"?>\r\n'
        xml_str += (
            '<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" '
            '"http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">\r\n'
        )
        xml_str += (
            '<svg version="1.1" id="" xmlns="http://www.w3.org/2000/svg" '
            'preserveAspectRatio="xMinYMin meet" '
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
        xml_str += '<g style="shape-rendering: ' + shape_rendering + ';">\r\n'
        xml_str += self.poly_placeholder
        xml_str += "</g>\r\n"
        xml_str += "<desc>" + self.svg_desc + "</desc>\r\n"
        xml_str += "</svg>"

        return xml_str

    def xml_poly(self, polygon: list):
        """Create polygon segments"""

        xml_final = ""
        for idx, part in enumerate(polygon):
            xml_poly = "<g>"
            poly = part["polygon"]
            colors = part["color"]

            for ip, poly_slice in enumerate(poly):
                # Check if image was substituted in broken polygon
                if isinstance(poly_slice, str):
                    xml_poly += poly_slice
                    continue

                hex_color = self.rgb2hex(colors[ip][0], colors[ip][1], colors[ip][2])

                xml_poly += (
                    '<path d="M'
                    + " ".join("%s,%s" % tup for tup in poly_slice)
                    + 'Z" fill="'
                    + hex_color
                    + '" fill-opacity="'
                    + str(colors[ip][3])
                    + '"/>'
                )
            xml_poly += "</g>"
            xml_final += xml_poly

        return xml_final

    def xml_setup_pattern(self):
        # Standard pattern
        xl = np.linspace(
            0,
            round(
                self.width
                * self.repeat_horizontal_spacing
                * self.repeat_horizontal_amount
            ),
            self.repeat_horizontal_amount + 1,
        ).tolist()[:-1]

        xli = xl
        if self.repeat_alternate >= 0:
            xli = [
                (v + self.single_polygon_x_center) * self.repeat_alternate for v in xl
            ]

        yl = np.linspace(
            0,
            round(
                self.height * self.repeat_vertical_spacing * self.repeat_vertical_amount
            ),
            self.repeat_vertical_amount + 1,
        ).tolist()[:-1]

        pattern_list = [[] for _ in yl]
        for iy in range(len(yl)):
            ix_list = []
            xll = xl
            if iy % 2 != 0:
                xll = xli
            for ix in range(len(xll)):
                ix_list.append(
                    (
                        self.single_polygon_x_center + xll[ix],
                        self.single_polygon_y_center + yl[iy],
                        {"broken": False},
                    )
                )

            pattern_list[iy] = ix_list

        if self.is_broken is False:
            return pattern_list

        # Equally distributed random items to break in pattern per line (vertical)
        broken_polygons = self._get_broken_polygons(
            self.broken_factor, self.repeat_vertical_amount
        )

        # Create a new distribution by skipping first 2 and last 2 rows.
        # This will make sure the pattern is 1) repeatable even though it is broken 2) closely respect broken factor.
        if self.repeat_broken_skip_edge is True:
            broken_polygons = (
                [0, 0]
                + self._get_broken_polygons(
                    self.broken_factor, self.repeat_vertical_amount - 4
                )
                + [0, 0]
            )

        for x, k in enumerate(pattern_list):
            broken_horizontal = broken_polygons[x]
            broken_count = 0
            while broken_count < broken_horizontal:
                pattern_list[x][self._random_index(pattern_list[x])][-1][
                    "broken"
                ] = True
                broken_count += 1

        return pattern_list

    def xml_create_pattern(self, polygons: list):
        xml_pattern = []
        for p in polygons:
            xml_pattern.append("<g>" + self.xml_poly(p) + "</g>")

        return {"paths": xml_pattern, "string": "\r\n".join(xml_pattern)}

    def save_svg(self, content) -> str:
        """Write string as SVG"""

        svg_file = f"{self.output_directory}/{_get_formatted_datetime()}_{self.output_file_name}.svg"
        text_file = open(svg_file, "wt")
        text_file.write(content)
        text_file.close()

        return svg_file

    def save_png(self, content) -> str:
        """Save SVG to PNG"""

        png_file = f"{self.output_directory}/{_get_formatted_datetime()}_{self.output_file_name}.png"
        svg2png(bytestring=content, write_to=png_file)

        return png_file

    # noinspection PyMethodMayBeStatic
    def join_list(self, x, deli=" ") -> str:
        """Join lists/tuples to string"""

        return deli.join(map(str, x))

    def rgb2hex(self, r, g, b) -> str:
        """RGB to Hexadecimal"""

        return "#{0:02x}{1:02x}{2:02x}".format(
            self._rgbounds(r), self._rgbounds(g), self._rgbounds(b)
        )

    # noinspection PyMethodMayBeStatic
    def _determine_external_svg_dimensions(self, xml_string) -> dict:

        svg_width = None
        match_width = re.search(
            r"<svg[^>]*width=[\"|\']{1}(?P<width>\d+(?:\.\d+)?)[\"|\']{1}[^>]*>",
            xml_string,
        )
        if match_width:
            svg_width = match_width.group("width")

        svg_height = None
        match_height = re.search(
            r"<svg[^>]*height=[\"|\']{1}(?P<height>\d+(?:\.\d+)?)[\"|\']{1}[^>]*>",
            xml_string,
        )
        if match_height:
            svg_height = match_height.group("height")

        match_viewbox = re.search(
            r"<svg[^>]*(?P<viewBox>viewBox=[\"|\']{1}(?P<minx>\d+(?:\.\d+)?)\s{1}(?P<miny>\d+(?:\.\d+)?)\s{1}("
            r"?P<width>\d+(?:\.\d+)?)\s{1}(?P<height>\d+(?:\.\d+)?)[\"|\']{1})[^>]*>",
            xml_string,
        )

        additional_svg_dimension_tags = []
        # If no "width" or "height" attribute was available in SVG, set it, else it won't be displayed in pattern.
        if svg_width is None:
            svg_width = match_viewbox.group("width")
            additional_svg_dimension_tags.append(f'width="{svg_width}"')

        if svg_height is None:
            svg_height = match_viewbox.group("height")
            additional_svg_dimension_tags.append(f'height="{svg_height}"')

        if additional_svg_dimension_tags:
            xml_string = xml_string.replace(
                match_viewbox.group("viewBox"),
                (
                    match_viewbox.group("viewBox")
                    + " "
                    + " ".join(additional_svg_dimension_tags)
                ),
            )

        return {
            "width": float(svg_width),
            "height": float(svg_height),
            "svg": xml_string,
        }

    # noinspection PyMethodMayBeStatic
    def _extract_svg_part(self, xml_string):

        match_svg = re.search(
            r"<svg\b[^>]*?>[\s\S]*?<\/svg>",
            xml_string,
        )

        if not match_svg:
            raise Exception(f"Could not extract `<svg>` tag from given input image.")

        return match_svg.group()

    # noinspection PyMethodMayBeStatic
    def _file_naming(self, data) -> str:
        """File naming based on preset options"""

        return "_".join(
            [
                "{}-{}".format(k, v)
                for k, v in data.items()
                if k not in ["repeat", "colors"]
            ]
        )

    # noinspection PyMethodMayBeStatic
    def _rgbounds(self, x) -> int:
        """RGB boundaries"""

        return max(0, min(x, 255))

    # noinspection PyMethodMayBeStatic
    def _check_viewbox(self, c) -> list:
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
    def _random_partition(self, n, s) -> list:
        partition = [0] * s
        for x in range(n):
            partition[random.randrange(s)] += 1

        return partition

    # noinspection PyMethodMayBeStatic
    def _random_index(self, n) -> int:
        if self.repeat_broken_skip_edge is True:
            return random.randrange(1, len(n) - 1)

        return random.randrange(len(n))

    def _get_broken_polygons(self, broken_total_factor, amount_in_partition) -> list:
        return [
            round(sum(x) / 2)
            for x in zip(
                self._random_partition(broken_total_factor, amount_in_partition),
                self._random_partition(broken_total_factor, amount_in_partition),
            )
        ]
