#
# Python Imaging Library
# $Id: //modules/pil/PIL/GimpPaletteFile.py#4 $
#
# stuff to read GIMP palette files
#
# History:
#       97-08-23 fl     Created
#
# Copyright (c) Secret Labs AB 1997.
# Copyright (c) Fredrik Lundh 1997.
#
# See the README file for information on usage and redistribution.
#

import string

##
# File handler for GIMP's palette format.

class GimpPaletteFile:

    rawmode = "RGB"

    def __init__(self, fp):

        self.palette = map(lambda i: chr(i)*3, range(256))

        if fp.readline()[:12] != "GIMP Palette":
            raise SyntaxError, "not a GIMP palette file"

        i = 0

        while i <= 255:

            s = fp.readline()

            if not s:
                break
            if len(s) > 100:
                raise SyntaxError, "bad palette file"

            if s[0] == "#":
                continue

            v = tuple(map(string.atoi, string.split(s)[:3]))
            if len(v) != 3:
                raise ValueError, "bad palette entry"

            if 0 <= i <= 255:
                self.palette[i] = chr(v[0]) + chr(v[1]) + chr(v[2])

            i = i + 1

        self.palette = string.join(self.palette, "")


    def getpalette(self):

        return self.palette, self.rawmode
