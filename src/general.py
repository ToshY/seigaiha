# -*- coding: utf-8 -*-
"""
Created on Sat Jul 25 14:20:54 2020

@author: ToishY
"""

import os
import datetime
from cairosvg import svg2png


class General:
    def __init__(self, path, file):
        # Working dirs / input
        self.cwd = path

        # Stem
        self.file_name = file

        # Output
        self.output_dir = self.dirs(self.cwd, "out")
        self.src_dir = self.dirs(self.cwd, "src")

        # Datetime
        self.date = datetime.datetime.now()
        self.datetime = self.date.strftime("%d-%m-%Y_%H-%M-%S")

    def dirs(self, main_dir, dir_name):
        return os.sep.join([main_dir, dir_name])

    def save_svg(self, content, ext=".svg"):
        """ Write string to file """

        my_file = os.sep.join(
            [self.output_dir, self.file_name + "_" + self.datetime + ext]
        )

        text_file = open(my_file, "wt")
        text_file.write(content)
        text_file.close()

        return my_file

    def save_png(self, content, ext=".png"):
        """ Save SVG as PNG """

        my_file = os.sep.join(
            [self.output_dir, self.file_name + "_" + self.datetime + ext]
        )

        svg2png(bytestring=content, write_to=my_file)

        return my_file
