#
# The Python Imaging Library.
# $Id: //modules/pil/PIL/ImageFile.py#8 $
#
# base class for image file handlers
#
# history:
# 1995-09-09 fl   Created
# 1996-03-11 fl   Fixed load mechanism.
# 1996-04-15 fl   Added pcx/xbm decoders.
# 1996-04-30 fl   Added encoders.
# 1996-12-14 fl   Added load helpers
# 1997-01-11 fl   Use encode_to_file where possible
# 1997-08-27 fl   Flush output in _save
# 1998-03-05 fl   Use memory mapping for some modes
# 1999-02-04 fl   Use memory mapping also for "I;16" and "I;16B"
# 1999-05-31 fl   Added image parser
# 2000-10-12 fl   Set readonly flag on memory-mapped images
# 2002-03-20 fl   Use better messages for common decoder errors
# 2003-04-21 fl   Fall back on mmap/map_buffer if map is not available
#
# Copyright (c) 1997-2002 by Secret Labs AB
# Copyright (c) 1995-2002 by Fredrik Lundh
#
# See the README file for information on usage and redistribution.
#

import Image
import traceback, sys, os

MAXBLOCK = 65536

ERRORS = {
    -1: "image buffer overrun error",
    -2: "decoding error",
    -3: "unknown error",
    -8: "bad configuration",
    -9: "out of memory error"
}

#
# --------------------------------------------------------------------
# Helpers

def _tilesort(t1, t2):
    # sort on offset
    return cmp(t1[2], t2[2])

#
# --------------------------------------------------------------------
# ImageFile base class

##
# Base class for image file handlers.

class ImageFile(Image.Image):
    "Base class for image file format handlers."

    def __init__(self, fp=None, filename=None):
        Image.Image.__init__(self)

        self.tile = None
        self.readonly = 1 # until we know better

        self.decoderconfig = ()
        self.decodermaxblock = MAXBLOCK

        if type(fp) == type(""):
            # filename
            self.fp = open(fp, "rb")
            self.filename = fp
        else:
            # stream
            self.fp = fp
            self.filename = filename

        try:
            self._open()
        except IndexError, v: # end of data
            if Image.DEBUG > 1:
                traceback.print_exc()
            raise SyntaxError, v
        except TypeError, v: # end of data (ord)
            if Image.DEBUG > 1:
                traceback.print_exc()
            raise SyntaxError, v
        except KeyError, v: # unsupported mode
            if Image.DEBUG > 1:
                traceback.print_exc()
            raise SyntaxError, v
        except EOFError, v: # got header but not the first frame
            if Image.DEBUG > 1:
                traceback.print_exc()
            raise SyntaxError, v

        if not self.mode or self.size[0] <= 0:
            raise SyntaxError, "not identified by this driver"

    def draft(self, mode, size):
        "Set draft mode"

        pass

    def verify(self):
        "Check file integrity"

        # raise exception if something's wrong.  must be called
        # directly after open, and closes file when finished.
        self.fp = None

    def load(self):
        "Load image data based on tile list"

        Image.Image.load(self)

        if self.tile is None:
            raise IOError("cannot load this image")
        if not self.tile:
            return

        self.map = None

        readonly = 0

        if self.filename and len(self.tile) == 1:
            # try memory mapping
            d, e, o, a = self.tile[0]
            if d == "raw" and a[0] == self.mode and a[0] in Image._MAPMODES:
                try:
                    if hasattr(Image.core, "map"):
                        # use built-in mapper
                        self.map = Image.core.map(self.filename)
                        self.map.seek(o)
                        self.im = self.map.readimage(
                            self.mode, self.size, a[1], a[2]
                            )
                    else:
                        # use mmap, if possible
                        import mmap
                        file = open(self.filename, "r+")
                        size = os.path.getsize(self.filename)
                        # FIXME: on Unix, use PROT_READ etc
                        self.map = mmap.mmap(file.fileno(), size)
                        self.im = Image.core.map_buffer(
                            self.map, self.size, d, e, o, a
                            )
                    readonly = 1
                except (AttributeError, IOError, ImportError):
                    self.map = None

        self.load_prepare()

        if not self.map:

            # sort tiles in file order
            self.tile.sort(_tilesort)

            try:
                # FIXME: This is a hack to handle TIFF's JpegTables tag.
                prefix = self.tile_prefix
            except AttributeError:
                prefix = ""

            for d, e, o, a in self.tile:
                d = Image._getdecoder(self.mode, d, a, self.decoderconfig)
                self.load_seek(o)
                try:
                    d.setimage(self.im, e)
                except ValueError:
                    continue
                b = prefix
                t = len(b)
                while 1:
                    s = self.load_read(self.decodermaxblock)
                    if not s:
                        self.tile = []
                        raise IOError("image file is truncated (%d bytes not processed)" % len(b))
                    b = b + s
                    n, e = d.decode(b)
                    if n < 0:
                        break
                    b = b[n:]
                    t = t + n

        self.tile = []
        self.readonly = readonly

        self.fp = None # might be shared

        if not self.map and e < 0:
            error = ERRORS.get(e, "decoder error %d" % e)
            raise IOError(error + " when reading image file")

        # post processing
        if hasattr(self, "tile_post_rotate"):
            # FIXME: This is a hack to handle rotated PCD's
            self.im = self.im.rotate(self.tile_post_rotate)
            self.size = self.im.size

        self.load_end()

    def load_prepare(self):
        # create image memory if necessary
        if not self.im or\
           self.im.mode != self.mode or self.im.size != self.size:
            self.im = Image.core.new(self.mode, self.size)
        # create palette (optional)
        if self.mode == "P":
            Image.Image.load(self)

    def load_end(self):
        # may be overridden
        pass

    def load_seek(self, pos):
        # may be overridden for contained formats
        self.fp.seek(pos)

    def load_read(self, bytes):
        # may be overridden for blocked formats (e.g. PNG)
        return self.fp.read(bytes)


class _ParserFile:
    # parser support class.

    def __init__(self, data):
        self.data = data
        self.offset = 0

    def close(self):
        self.data = self.offset = None

    def tell(self):
        return self.offset

    def seek(self, offset, whence=0):
        if whence == 0:
            self.offset = offset
        elif whence == 1:
            self.offset = self.offset + offset
        else:
            # force error in Image.open
            raise IOError("illegal argument to seek")

    def read(self, bytes=0):
        pos = self.offset
        if bytes:
            data = self.data[pos:pos+bytes]
        else:
            data = self.data[pos:]
        self.offset = pos + len(data)
        return data

    def readline(self):
        # FIXME: this is slow!
        s = ""
        while 1:
            c = self.read(1)
            if not c:
                break
            s = s + c
            if c == "\n":
                break
        return s

class Parser:
    # incremental image parser.  implements the consumer
    # interface.

    image = None
    data = None
    decoder = None
    finished = 0

    def reset(self):
        assert self.data is None, "cannot reuse parsers"

    def feed(self, data):
        # collect data

        if self.finished:
            return

        if self.data is None:
            self.data = data
        else:
            self.data = self.data + data

        # parse what we have
        if self.decoder:

            if self.offset > 0:
                # skip header
                skip = min(len(self.data), self.offset)
                self.data = self.data[skip:]
                self.offset = self.offset - skip
                if self.offset > 0 or not self.data:
                    return

            n, e = self.decoder.decode(self.data)

            if n < 0:
                # end of stream
                self.data = None
                self.finished = 1
                if e < 0:
                    # decoding error
                    self.image = None
                    error = ERRORS.get(e, "decoder error %d" % e)
                    raise IOError(error + " when reading image file")
                else:
                    # end of image
                    return
            self.data = self.data[n:]

        else:

            # attempt to open this file
            try:
                try:
                    fp = _ParserFile(self.data)
                    im = Image.open(fp)
                finally:
                    fp.close() # explicitly close the virtual file
            except IOError:
                pass # not enough data
            else:

                # sanity check
                if len(im.tile) != 1:
                    raise IOError("cannot parse this image")

                # initialize decoder
                im.load_prepare()
                d, e, o, a = im.tile[0]
                im.tile = []
                self.decoder = Image._getdecoder(
                    im.mode, d, a, im.decoderconfig
                    )
                self.decoder.setimage(im.im, e)

                # calculate decoder offset
                self.offset = o
                if self.offset <= len(self.data):
                    self.data = self.data[self.offset:]
                    self.offset = 0

                self.image = im

    def close(self):
        # finish decoding
        if self.decoder:
            # get rid of what's left in the buffers
            self.feed("")
            self.data = self.decoder = None
            if not self.finished:
                raise IOError("image was incomplete")
        if not self.image:
            raise IOError("cannot parse this image")
        return self.image

#
# --------------------------------------------------------------------
# Save image body

def _save(im, fp, tile):
    "Helper to save image based on tile list"

    im.load()
    if not hasattr(im, "encoderconfig"):
        im.encoderconfig = ()
    tile.sort(_tilesort)
    bufsize = max(MAXBLOCK, im.size[0] * 4) # see RawEncode.c
    try:
        fh = fp.fileno()
        fp.flush()
    except AttributeError:
        # compress to Python file-compatible object
        for e, b, o, a in tile:
            e = Image._getencoder(im.mode, e, a, im.encoderconfig)
            if o > 0:
                fp.seek(o, 0)
            e.setimage(im.im, b)
            while 1:
                l, s, d = e.encode(bufsize)
                fp.write(d)
                if s:
                    break
            if s < 0:
                raise IOError("encoder error %d when writing image file" % s)
    else:
        # slight speedup: compress to real file object
        for e, b, o, a in tile:
            e = Image._getencoder(im.mode, e, a, im.encoderconfig)
            if o > 0:
                fp.seek(o, 0)
            e.setimage(im.im, b)
            s = e.encode_to_file(fh, bufsize)
            if s < 0:
                raise IOError("encoder error %d when writing image file" % s)
    try:
        fp.flush()
    except: pass
