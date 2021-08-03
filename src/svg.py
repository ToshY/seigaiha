# -*- coding: utf-8 -*-
"""
Created on Wed Jul 22 16:29:25 2020

@author: ToshY
"""

import datetime
import random
import numpy as np
from cairosvg import svg2png


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
        
        # Spacing and factor
        self.xnodes = data['repeat']['horizontal']['amount']
        self.xspacing_factor = data['repeat']['horizontal']['spacing']
        self.ynodes = data['repeat']['vertical']['amount']
        self.yspacing_factor = data['repeat']['vertical']['spacing']

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

        # TODO; Fix the width for patterns + translate/normalize to top left ?
        xml_str = '<?xml version="1.0" encoding="UTF-8"?>\r\n'
        xml_str += '<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">\r\n'
        xml_str += '<svg version="1.1" id="" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" preserveAspectRatio="xMidYMid meet" '
        xml_str += (
            'width="' + str(self.width) + 'px" height="' + str(self.height) + 'px" '
        )
        xml_str += 'viewBox="' + self.join_list(self.view_box) + '">\r\n'
        xml_str += '<g style="shape-rendering:' + shape_rendering + ';">\r\n'
        xml_str += self.poly_placeholder
        xml_str += "</g>\r\n"
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

        # TODO: This part is still a bit wonky. The viewbox is not exactly fitting the pattern yet.
        # So I don't know how to fix it yet. The whole viewBox thing below was just a test also
        # which I came up while drinking so, it works somehow.
        viewBox = self.view_box
        viewBox[0] = viewBox[0] + self.width
        viewBox[1] = viewBox[1] + self.height
        viewBox[2] = viewBox[2] * self.xnodes - self.width
        viewBox[3] = viewBox[3] / self.ynodes

        xml_str = '<?xml version="1.0" encoding="UTF-8"?>\r\n'
        xml_str += '<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">\r\n'
        xml_str += '<svg version="1.1" id="" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" preserveAspectRatio="xMinYMin" '
        xml_str += (
            'width="' + str(self.width*self.xspacing_factor) + 'px" height="' + str(self.height*self.yspacing_factor) + 'px" '
        )
        xml_str += 'viewBox="' + self.join_list(viewBox) + '">\r\n'
        xml_str += '<g style="shape-rendering:' + shape_rendering + ';">\r\n'
        xml_str += self.poly_placeholder
        xml_str += "</g>\r\n"
        xml_str += "</svg>"

        return xml_str

    def xml_poly(self, polygon, colours):
        """ Create polygon segments """

        # Loop over points and format to svg polygon
        xml_final = ""
        for idx, s in enumerate(polygon):
            xml_poly = "<g>"
            for ip, p in enumerate(s[:-1]):
                c = colours[ip]
                 # Get HEX colours
                chex = self.rgb2hex(c[3], c[2], c[1])
                
                xml_poly += (
                    '<path d="M'
                    + " ".join("%s,%s" % tup for tup in p)
                    + 'Z" fill="'
                    + chex
                    + '" fill-opacity="'
                    + str(c[0])
                    + '"/>'
                )
            xml_poly += '</g>'
            xml_final += xml_poly

        return xml_final
    
    def xml_poly_pattern(self, polygon, colours, broken_colours):
        """ Create polygon segments """

        # Loop over points and format to svg polygon
        xml_final = ""
        for idx, s in enumerate(polygon):
            is_broken = s[-1]['broken']
            xml_poly = "<g>"
            for ip, p in enumerate(s[:-1]):
                c = colours[ip]
                 # Get HEX colours
                chex = self.rgb2hex(c[3], c[2], c[1])
                if is_broken is True:
                    c = broken_colours[ip]
                    chex = self.rgb2hex(c[3], c[2], c[1])
                
                xml_poly += (
                    '<path d="M'
                    + " ".join("%s,%s" % tup for tup in p)
                    + 'Z" fill="'
                    + chex
                    + '" fill-opacity="'
                    + str(c[0])
                    + '"/>'
                )
            xml_poly += '</g>'
            xml_final += xml_poly

        return xml_final

    def xml_setup_pattern(self, pattern_info):
        hz = pattern_info["horizontal"]
        vt = pattern_info["vertical"]
        br = pattern_info["broken"]
        at = pattern_info["alternate"]

        # Standard pattern
        xl = np.linspace(
            0, round(self.width * hz["spacing"] * hz["amount"]), hz["amount"] + 1
        ).tolist()[:-1]

        xli = xl
        if at >= 0:
            xli = [(v + self.xcenter) * at for v in xl]

        yl = np.linspace(
            0, round(self.height * vt["spacing"] * vt["amount"]), vt["amount"] + 1
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
        if not br['factor']:
            raise Exception(
                "The broken factor was not specified."
            )
        btf = round(br['factor'] * (hz["amount"] * vt["amount"]))

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
                    pattern_list[x][self._random_index(pattern_list[x])][-1][
                        "broken"
                    ] = True
                    bk += 1

        # Pattern list to fill polygons with
        return pattern_list

    def xml_create_pattern(self, polygons, colours, broken_colours):
        xml_pattern = []
        for p in polygons:
            xml_pattern.append(self.xml_poly_pattern(p, colours, broken_colours))
        return {"paths": xml_pattern, "string": "\r\n".join(xml_pattern)}

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
