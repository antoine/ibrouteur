#
# THIS IS WORK IN PROGRESS.
#
# The Python Imaging Library.
# $Id: //modules/pil/PIL/WmfImagePlugin.py#4 $
#
# WMF support for PIL
#
# history:
#       96-12-14 fl     Created
#
# notes:
#       This code currently supports placable metafiles only, and
#       just a few graphics operations are implemented.
#
# Copyright (c) Secret Labs AB 1997.
# Copyright (c) Fredrik Lundh 1996.
#
# See the README file for information on usage and redistribution.
#

__version__ = "0.1"

import Image, ImageDraw, ImageFile
import string

#
# --------------------------------------------------------------------

def i16(c):
    return ord(c[0]) + (ord(c[1])<<8)

def i32(c):
    return ord(c[0]) + (ord(c[1])<<8) + (ord(c[2])<<16) + (ord(c[3])<<24)

# --------------------------------------------------------------------
# The following codes are taken from the wingdi.h header file.
# Copyright (c) 1985-1996, Microsoft Corp.  All rights reserved.

META_ANIMATEPALETTE = 0x0436
META_ARC = 0x0817
META_BITBLT = 0x0922
META_CHORD = 0x0830
META_CREATEBRUSHINDIRECT = 0x02FC
META_CREATEFONTINDIRECT = 0x02FB
META_CREATEPALETTE = 0x00f7
META_CREATEPATTERNBRUSH = 0x01F9
META_CREATEPENINDIRECT = 0x02FA
META_CREATEREGION = 0x06FF
META_DELETEOBJECT = 0x01f0
META_DIBBITBLT = 0x0940
META_DIBCREATEPATTERNBRUSH = 0x0142
META_DIBSTRETCHBLT = 0x0b41
META_ELLIPSE = 0x0418
META_ESCAPE = 0x0626
META_EXCLUDECLIPRECT = 0x0415
META_EXTFLOODFILL = 0x0548
META_EXTTEXTOUT = 0x0a32
META_FILLREGION = 0x0228
META_FLOODFILL = 0x0419
META_FRAMEREGION = 0x0429
META_INTERSECTCLIPRECT = 0x0416
META_INVERTREGION = 0x012A
META_LINETO = 0x0213
META_MOVETO = 0x0214
META_OFFSETCLIPRGN = 0x0220
META_OFFSETVIEWPORTORG = 0x0211
META_OFFSETWINDOWORG = 0x020F
META_PAINTREGION = 0x012B
META_PATBLT = 0x061D
META_PIE = 0x081A
META_POLYGON = 0x0324
META_POLYLINE = 0x0325
META_POLYPOLYGON = 0x0538
META_REALIZEPALETTE = 0x0035
META_RECTANGLE = 0x041B
META_RESIZEPALETTE = 0x0139
META_RESTOREDC = 0x0127
META_ROUNDRECT = 0x061C
META_SAVEDC = 0x001E
META_SCALEVIEWPORTEXT = 0x0412
META_SCALEWINDOWEXT = 0x0410
META_SELECTCLIPREGION = 0x012C
META_SELECTOBJECT = 0x012D
META_SELECTPALETTE = 0x0234
META_SETBKCOLOR = 0x0201
META_SETBKMODE = 0x0102
META_SETDIBTODEV = 0x0d33
META_SETMAPMODE = 0x0103
META_SETMAPPERFLAGS = 0x0231
META_SETPALENTRIES = 0x0037
META_SETPIXEL = 0x041F
META_SETPOLYFILLMODE = 0x0106
META_SETRELABS = 0x0105
META_SETROP2 = 0x0104
META_SETSTRETCHBLTMODE = 0x0107
META_SETTEXTALIGN = 0x012E
META_SETTEXTCHAREXTRA = 0x0108
META_SETTEXTCOLOR = 0x0209
META_SETTEXTJUSTIFICATION = 0x020A
META_SETVIEWPORTEXT = 0x020E
META_SETVIEWPORTORG = 0x020D
META_SETWINDOWEXT = 0x020C
META_SETWINDOWORG = 0x020B
META_STRETCHBLT = 0x0B23
META_STRETCHDIB = 0x0f43
META_TEXTOUT = 0x0521

# create a code to name dictionary (for debugging)
NAME = {}
for k, v in vars().items():
    if k[:5] == "META_":
        NAME[v] = k[5:]

#
# --------------------------------------------------------------------
# Read WMF file

def _accept(prefix):
    return prefix[:6] == "\327\315\306\232\000\000"

##
# Image plugin for Windows metafiles.  This plugin can identify a
# metafile, but the loader only supports a small number of primitives,
# and isn't very usable.

class WmfImageFile(ImageFile.ImageFile):

    format = "WMF"
    format_description = "Windows Metafile"

    def _open(self):

        # check placable header
        s = self.fp.read(22)
        if s[:6] != "\327\315\306\232\000\000":
            raise SyntaxError, "Not a placable WMF file"

        # position on output device
        bbox = i16(s[6:8]), i16(s[8:10]), i16(s[10:12]), i16(s[12:14])

        # FIXME: should take the scale into account

        self.mode = "P"
        self.size = (bbox[2]-bbox[0]) / 20, (bbox[3]-bbox[1]) / 20

        # FIXME: while hacking
        self.size = (bbox[2] + bbox[0])/10, (bbox[3] + bbox[1])/10

        self.bbox = bbox

        # check standard header
        s = self.fp.read(18)
        if s[:6] != "\001\000\011\000\000\003":
            raise SyntaxError, "Not a WMF file"

    def _ink(self, rgb):

        # lookup colour in current palette
        try:
            return self.palette[rgb]
        except KeyError:
            # hmm. what if the palette becomes full?
            ink = len(self.palette)
            self.palette[rgb] = ink
            return ink

    def load(self):

        if self.im:
            return

        #
        # windows standard palette

        self.palette = {
            '\000\000\000': 0,
            '\200\000\000': 1,
            '\000\200\000': 2,
            '\200\200\000': 3,
            '\000\000\200': 4,
            '\200\000\200': 5,
            '\000\200\200': 6,
            '\300\300\300': 7,
            '\300\334\300': 8,
            '\246\312\360': 9,
            '\377\373\360': 246,
            '\240\240\244': 247,
            '\200\200\200': 248,
            '\377\000\000': 249,
            '\000\377\000': 250,
            '\377\377\000': 251,
            '\000\000\377': 252,
            '\377\000\377': 253,
            '\000\377\377': 254,
            '\377\377\377': 255,
        }

        fill = 0

        pen = brush = self._ink("\000\000\000")
        paper = self._ink("\377\377\377")

        self.im = Image.core.fill(self.mode, self.size, paper)

        #
        # render metafile into image, using the standard palette

        id = ImageDraw.ImageDraw(self)

        while 1:

            s = self.fp.read(6)

            size = i32(s)*2
            func = i16(s[4:])

            if not func:
                break

            s = self.fp.read(size-6)

            if func == META_SETPOLYFILLMODE:
                fill = i16(s)
                id.setfill(fill)

            elif func == META_CREATEBRUSHINDIRECT:
                brush = self._ink(s[2:5])

            elif func == META_CREATEPENINDIRECT:
                pen = self._ink(s[6:9])

            elif func == META_POLYGON:
                xy = map(lambda i,s=s: i16(s[i:i+2])/10, range(2, len(s), 2))
                if fill:
                    id.setink(brush)
                    id.polygon(xy)
                    id.setink(pen)
                    id.setfill(0)
                    id.polygon(xy)
                    id.setfill(1)
                else:
                    id.setink(pen)
                    id.polygon(xy)

            elif func == META_POLYLINE:
                xy = map(lambda i,s=s: i16(s[i:i+2])/10, range(2, len(s), 2))
                id.setink(pen)
                id.line(xy)

            elif func == META_RECTANGLE:
                xy = (i16(s[2:4])/10, i16(s[0:2])/10,
                      i16(s[6:8])/10, i16(s[4:6])/10)
                if fill:
                    id.setink(brush)
                    id.rectangle(xy)
                    id.setink(pen)
                    id.setfill(0)
                    id.rectangle(xy)
                    id.setfill(1)
                else:
                    id.setink(pen)
                    id.rectangle(xy)
            else:
                if Image.DEBUG:
                    print size, hex(func), NAME[func]
                pass

        #
        # attach palette to image

        palette = ["\0\0\0"] * 256
        for rgb, i in self.palette.items():
            if i < 256:
                palette[i] = rgb
        self.im.putpalette("RGB", string.join(palette, ""))

#
# --------------------------------------------------------------------
# Registry stuff

Image.register_open("WMF", WmfImageFile, _accept)

Image.register_extension("WMF", ".wmf")
