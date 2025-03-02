import json
import re
import base64
import datetime
import random
from pathlib import Path

import numpy as np
from cairocffi import CairoError  # type: ignore[import-untyped]
from cairosvg import svg2png  # type: ignore[import-untyped]

from seigaiha.exception import InvalidViewBoxError, SvgToPngImageError


def _get_formatted_datetime():
    """
    Get formatted datetime.
    """

    return datetime.datetime.now().strftime("%d-%m-%Y_%H-%M-%S-%f")


class SVGmaker:
    """
    SVG maker.
    """

    poly_placeholder = "%polygons%"

    svg_description = "Rendered with Seigaiha | https://github.com/ToshY/seigaiha"

    def __init__(
        self,
        user_preset: dict,
        image_dimensions: list,
        image_view_box: list = [0, 0, -1, -1],
    ):
        self.preset = user_preset
        self.safe_base_encoded_preset = base64.b64encode(
            json.dumps(self.preset).encode("utf-8")
        ).decode("utf-8")

        # Initial image dimensions
        self.width, self.height = image_dimensions

        # Center polygon
        self.single_polygon_x_center = self.width / 2
        self.single_polygon_y_center = self.height / 2

        # Viewbox
        self.view_box = self._check_viewbox_dimensions(image_view_box)
        if self.view_box[-2:] == [-1, -1]:
            self.view_box[-2:] = image_dimensions

        # Pattern
        pattern = user_preset.get("pattern", False)
        if pattern:
            # Alternate
            self.repeat_alternate = pattern.get("alternate", 1)

            # Amount and spacing
            self.repeat_horizontal = pattern.get(
                "horizontal", {"amount": None, "spacing": None}
            )
            self.repeat_horizontal_amount = self.repeat_horizontal.get("amount", None)
            self.repeat_horizontal_spacing = self.repeat_horizontal.get("spacing", None)
            self.repeat_vertical = pattern.get(
                "vertical", {"amount": None, "spacing": None}
            )
            self.repeat_vertical_amount = self.repeat_vertical.get("amount", None)
            self.repeat_vertical_spacing = self.repeat_vertical.get("spacing", None)

            self.repeat_broken_factor = pattern.get("broken", {"factor": None}).get(
                "factor"
            )
            self.repeat_broken_factor_rounding = pattern.get(
                "broken", {"factor_rounding": "round"}
            ).get("factor_rounding")

            # Skip edges so they do not contain any broken elements
            self.repeat_broken_skip_edge = pattern.get(
                "broken", {"skip_edge": True}
            ).get("skip_edge")

            # Image placeholder
            self.repeat_broken_images = pattern.get("broken", {"images": []}).get(
                "images"
            )
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
            if self.repeat_broken_factor:
                self.is_broken = True
                if self.repeat_broken_factor > 0:
                    self.broken_factor = self.repeat_broken_factor

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

    def xml_initialise(self) -> str:
        xml_string = '<?xml version="1.0" encoding="UTF-8"?>\r\n'
        xml_string += (
            '<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" '
            '"http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">\r\n'
        )
        xml_string += (
            '<svg version="1.1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" preserveAspectRatio="'
            + self.preset.get("output", {})
            .get("svg", {})
            .get("preserveAspectRatio", "xMinYMin meet")
            + '" '
        )
        xml_string += (
            'width="' + str(self.width) + 'px" height="' + str(self.height) + 'px" '
        )
        xml_string += 'viewBox="' + self._join_view_box_list(self.view_box) + '">\r\n'
        xml_string += (
            '<g style="shape-rendering: '
            + self.preset.get("output", {})
            .get("svg", {})
            .get("style", {})
            .get("shape-rendering", "geometricPrecision")
            + ';">\r\n'
        )
        xml_string += self.poly_placeholder
        xml_string += "</g>\r\n"
        xml_string += (
            "<desc>"
            + self.svg_description
            + " | Created at: "
            + _get_formatted_datetime()
            + " | Options: "
            + self.safe_base_encoded_preset
            + "</desc>"
        )
        xml_string += "</svg>"

        return xml_string

    def xml_initialise_pattern(self) -> str:
        """
        Init XML pattern.
        """
        view_box = self.view_box
        view_box[0] = view_box[0] + self.width
        view_box[1] = view_box[1] + self.height
        view_box[2] = view_box[2] * self.repeat_horizontal_amount - self.width
        view_box[3] = view_box[3] / self.repeat_vertical_amount

        xml_string = '<?xml version="1.0" encoding="UTF-8"?>\r\n'
        xml_string += (
            '<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" '
            '"http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">\r\n'
        )
        xml_string += (
            '<svg version="1.1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" preserveAspectRatio="'
            + self.preset.get("output", {})
            .get("svg", {})
            .get("preserveAspectRatio", "xMinYMin meet")
            + '" '
        )
        xml_string += (
            'width="'
            + str(self.pattern_width)
            + 'px" '
            + 'height="'
            + str(self.pattern_height)
            + 'px" '
        )
        xml_string += 'viewBox="' + self._join_view_box_list(view_box) + '">\r\n'
        xml_string += (
            '<g style="shape-rendering: '
            + self.preset.get("output", {})
            .get("svg", {})
            .get("style", {})
            .get("shape-rendering", "geometricPrecision")
            + ';">\r\n'
        )
        xml_string += self.poly_placeholder
        xml_string += "</g>\r\n"
        xml_string += (
            "<desc>"
            + self.svg_description
            + " | Created at: "
            + _get_formatted_datetime()
            + " | Options: "
            + self.safe_base_encoded_preset
            + "</desc>"
        )
        xml_string += "</svg>"

        return xml_string

    def xml_polygon_points(self, polygons_and_colours: list):
        """Create polygon segments"""

        xml_final = ""
        for _, part in enumerate(polygons_and_colours):
            xml_poly = "<g>"
            poly = part["polygon"]
            colours = part["colour"]

            for current_index_polygon, poly_slice in enumerate(poly):
                # Check if image was substituted in broken polygon
                if isinstance(poly_slice, str):
                    xml_poly += poly_slice
                    continue

                polygon_hexadecimal_colours = self.rgb_to_hexadecimal_notation(
                    colours[current_index_polygon][0],
                    colours[current_index_polygon][1],
                    colours[current_index_polygon][2],
                )

                xml_poly += (
                    '<path d="M'
                    + " ".join("%s,%s" % tup for tup in poly_slice)
                    + 'Z" fill="'
                    + polygon_hexadecimal_colours
                    + '" fill-opacity="'
                    + str(colours[current_index_polygon][3])
                    + '"/>'
                )
            xml_poly += "</g>"
            xml_final += xml_poly

        return xml_final

    def xml_setup_pattern(self):
        """Setup pattern"""
        x_linspace = np.linspace(
            0,
            round(
                self.width
                * self.repeat_horizontal_spacing
                * self.repeat_horizontal_amount
            ),
            self.repeat_horizontal_amount + 1,
        ).tolist()[:-1]

        x_linspace_alt = x_linspace
        if self.repeat_alternate >= 0:
            x_linspace_alt = [
                (v + self.single_polygon_x_center) * self.repeat_alternate
                for v in x_linspace
            ]

        y_linspace = np.linspace(
            0,
            round(
                self.height * self.repeat_vertical_spacing * self.repeat_vertical_amount
            ),
            self.repeat_vertical_amount + 1,
        ).tolist()[:-1]

        pattern_list = [[] for _ in y_linspace]
        for current_y_index, _ in enumerate(y_linspace):
            ix_list = []
            xll = x_linspace
            if current_y_index % 2 != 0:
                xll = x_linspace_alt
            for _, current_x_value in enumerate(xll):
                ix_list.append(
                    (
                        self.single_polygon_x_center + current_x_value,
                        self.single_polygon_y_center + y_linspace[current_y_index],
                        {"broken": False, "edge": False, "invisible_edge": False},
                    )
                )

            pattern_list[current_y_index] = ix_list

        x_boundary = {"low": pattern_list[0][0][0], "high": pattern_list[-2][-1][0]}
        y_boundary = {"low": pattern_list[1][0][1], "high": pattern_list[-1][-1][1]}

        total_visible_count = 0
        complete_index_collection = []
        non_edge_index_collection = []
        for row, item in enumerate(pattern_list):
            for column, coord_tuple_collection in enumerate(item):
                if (
                    coord_tuple_collection[0] < x_boundary["low"]
                    or coord_tuple_collection[0] > x_boundary["high"]
                    or coord_tuple_collection[1] < y_boundary["low"]
                    or coord_tuple_collection[1] > y_boundary["high"]
                ):
                    pattern_list[row][column][-1]["edge"] = True
                    pattern_list[row][column][-1]["invisible_edge"] = True
                    continue

                if (
                    coord_tuple_collection[0] <= x_boundary["low"]
                    or coord_tuple_collection[0] >= x_boundary["high"]
                    or coord_tuple_collection[1] <= y_boundary["low"]
                    or coord_tuple_collection[1] >= y_boundary["high"]
                ):

                    pattern_list[row][column][-1]["edge"] = True
                    complete_index_collection.append((row, column))

                    total_visible_count += 1
                    continue

                total_visible_count += 1
                non_edge_index_collection.append((row, column))
                complete_index_collection.append((row, column))

        if self.is_broken is False:
            return pattern_list

        max_amount_broken_polygons = int(
            self._round_value(self.broken_factor * total_visible_count)
        )

        random.seed(self.preset.get("seed", None))
        sampled_broken_list = random.sample(
            complete_index_collection, max_amount_broken_polygons
        )
        if self.repeat_broken_skip_edge:
            non_edge_count = len(non_edge_index_collection)
            if non_edge_count < max_amount_broken_polygons:
                max_amount_broken_polygons = non_edge_count

            sampled_broken_list = random.sample(
                non_edge_index_collection, max_amount_broken_polygons
            )

        for broken_index_first_layer, broken_index_second_layer in sampled_broken_list:
            pattern_list[broken_index_first_layer][broken_index_second_layer][-1][
                "broken"
            ] = True

        return pattern_list

    def xml_create_pattern(self, polygons: list):
        """Create XML pattern"""

        xml_pattern = []
        for current_polygon in polygons:
            xml_pattern.append(
                "<g>" + self.xml_polygon_points(current_polygon) + "</g>"
            )

        return {"paths": xml_pattern, "string": "\r\n".join(xml_pattern)}

    def xml_result(self, polygon_output) -> str:
        svg_str = self.xml_initialise()
        svg_poly = self.xml_polygon_points(polygon_output)

        return svg_str.replace(self.poly_placeholder, svg_poly)

    def prepare_output_path(
        self,
        input_file,
        output_path,
        output_extension,
        unique_output_file_name: bool = False,
        file_prefix: str = "",
    ) -> Path:
        output_extension_with_leading_dot = "." + output_extension.lstrip(".")
        if output_path.is_dir():
            output_file = output_path.joinpath(
                input_file.stem + output_extension_with_leading_dot
            )
        else:
            output_file = Path(
                f"{output_path.with_suffix('')}{output_extension_with_leading_dot}"
            )

        # Use file prefix in output filename
        output_file = Path(
            f"{output_file.with_suffix('')}{'_' + file_prefix if file_prefix else ''}{output_extension_with_leading_dot}"
        )

        if unique_output_file_name:
            output_file = f"{output_file.with_suffix('')}_{_get_formatted_datetime()}{output_extension_with_leading_dot}"

        return output_file

    def save_svg(self, content, output_path: Path) -> None:
        text_file = open(str(output_path), "wt")
        text_file.write(content)
        text_file.close()

    def save_png(self, content, output_path: Path) -> None:
        try:
            svg2png(bytestring=content, write_to=str(output_path))
        except CairoError as e:
            raise SvgToPngImageError(str(e))

    # noinspection PyMethodMayBeStatic
    def _join_view_box_list(self, view_box, deli=" ") -> str:
        """Join lists/tuples to string"""

        return deli.join(map(str, view_box))

    def rgb_to_hexadecimal_notation(self, red_value, green_value, blue_value) -> str:
        """RGB to Hexadecimal"""

        return "#{0:02x}{1:02x}{2:02x}".format(
            self._rgb_boundary(red_value),
            self._rgb_boundary(green_value),
            self._rgb_boundary(blue_value),
        )

    # noinspection PyMethodMayBeStatic
    def _rgb_boundary(self, integer_value) -> int:
        """RGB boundaries"""

        return max(0, min(integer_value, 255))

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
            svg_width = match_viewbox.group("width")  # type: ignore[union-attr]
            additional_svg_dimension_tags.append(f'width="{svg_width}"')

        if svg_height is None:
            svg_height = match_viewbox.group("height")  # type: ignore[union-attr]
            additional_svg_dimension_tags.append(f'height="{svg_height}"')

        if additional_svg_dimension_tags:
            xml_string = xml_string.replace(
                match_viewbox.group("viewBox"),  # type: ignore[union-attr]
                (
                    match_viewbox.group("viewBox")  # type: ignore[union-attr]
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
            raise Exception("Could not extract `<svg>` tag from given input image.")

        return match_svg.group()

    # noinspection PyMethodMayBeStatic
    def _check_viewbox_dimensions(self, view_box_dimensions) -> list:
        """Check viewbox numerical values"""

        view_box = [s for s in view_box_dimensions if isinstance(s, (int, float))]
        if len(view_box) != len(view_box_dimensions):
            raise InvalidViewBoxError

        return view_box

    # noinspection PyMethodMayBeStatic
    def _round_value(self, val) -> int:
        match self.repeat_broken_factor_rounding:
            case "floor":
                return np.floor(val)
            case "ceil":
                return np.ceil(val)
            case _:
                return np.round(val)
