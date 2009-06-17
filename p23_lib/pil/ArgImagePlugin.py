#
# THIS IS WORK IN PROGRESS
#
# The Python Imaging Library.
# $Id: //modules/pil/PIL/ArgImagePlugin.py#3 $
#
# ARG animation support code
#
# history:
#       96-12-30 fl     Created
#       96-01-06 fl     Added safe scripting environment
#       96-01-10 fl     Added JHDR, UHDR and sYNC support
#
# Copyright (c) Secret Labs AB 1997.
# Copyright (c) Fredrik Lundh 1996-97.
#
# See the README file for information on usage and redistribution.
#

__version__ = "0.3"

import marshal, rexec, string

import Image, ImageFile, ImagePalette

from PngImagePlugin import i16, i32, ChunkStream, _MODES

MAGIC = "\212ARG\r\n\032\n"

APPLET_HOOK = None # must be explicitly enabled to support embedded scripts

# --------------------------------------------------------------------
# ARG parser

class ArgStream(ChunkStream):
    "Parser callbacks for ARG data"

    def __init__(self, fp):

        ChunkStream.__init__(self, fp)

        self.eof = 0

        self.im = None
        self.palette = None

        self.__reset()

    def __reset(self):

        # reset decoder state (called on init and sync)

        self.count = 0
        self.id = None
        self.action = ("NONE",)

        self.images = {}
        self.names = {}

        self.applets = {} # level 2


    def chunk_AHDR(self, offset, bytes):
        "AHDR -- animation header"

        # assertions
        if self.count != 0:
            raise SyntaxError, "misplaced AHDR chunk"

        s = self.fp.read(bytes)
        self.size = i32(s), i32(s[4:])
        try:
            self.mode, self.rawmode = _MODES[(ord(s[8]), ord(s[9]))]
        except:
            raise SyntaxError, "unknown ARG mode"

        if Image.DEBUG:
            print "AHDR size", self.size
            print "AHDR mode", self.mode, self.rawmode

        return s

    def chunk_AFRM(self, offset, bytes):
        "AFRM -- next frame follows"

        # assertions
        if self.count != 0:
            raise SyntaxError, "misplaced AFRM chunk"

        self.show = 1
        self.id = 0
        self.count = 1
        self.repair = None

        s = self.fp.read(bytes)
        if len(s) >= 2:
            self.id = i16(s)
            if len(s) >= 4:
                self.count = i16(s[2:4])
                if len(s) >= 6:
                    self.repair = i16(s[4:6])
                else:
                    self.repair = None

        if Image.DEBUG:
            print "AFRM", self.id, self.count

        return s

    def chunk_ADEF(self, offset, bytes):
        "ADEF -- store image"

        # assertions
        if self.count != 0:
            raise SyntaxError, "misplaced ADEF chunk"

        self.show = 0
        self.id = 0
        self.count = 1
        self.repair = None

        s = self.fp.read(bytes)
        if len(s) >= 2:
            self.id = i16(s)
            if len(s) >= 4:
                self.count = i16(s[2:4])

        if Image.DEBUG:
            print "ADEF", self.id, self.count

        return s

    def chunk_NAME(self, offset, bytes):
        "NAME -- name the current image"

        # assertions
        if self.count == 0:
            raise SyntaxError, "misplaced NAME chunk"

        name = self.fp.read(bytes)
        self.names[self.id] = name

        return name

    def chunk_AEND(self, offset, bytes):
        "AEND -- end of animation"

        if Image.DEBUG:
            print "AEND"

        self.eof = 1

        raise EOFError, "end of ARG file"

    def __getmodesize(self, s, full=1):

        size = i32(s), i32(s[4:])

        try:
            mode, rawmode = _MODES[(ord(s[8]), ord(s[9]))]
        except:
            raise SyntaxError, "unknown image mode"

        if full:
            if ord(s[12]):
                pass # interlace not yet supported
            if ord(s[11]):
                raise SyntaxError, "unknown filter category"

        return size, mode, rawmode

    def chunk_PAST(self, offset, bytes):
        "PAST -- paste one image into another"

        # assertions
        if self.count == 0:
            raise SyntaxError, "misplaced PAST chunk"

        if self.repair is not None:
            # we must repair the target image before we
            # start pasting

            # brute force; a better solution would be to
            # update only the dirty rectangles in images[id].
            # note that if images[id] doesn't exist, it must
            # be created

            self.images[self.id] = self.images[self.repair].copy()
            self.repair = None

        s = self.fp.read(bytes)
        im = self.images[i16(s)]
        x, y = i32(s[2:6]), i32(s[6:10])
        bbox = x, y, im.size[0]+x, im.size[1]+y

        if im.mode in ["RGBA"]:
            # paste with transparency
            # FIXME: should handle P+transparency as well
            self.images[self.id].paste(im, bbox, im)
        else:
            # paste without transparency
            self.images[self.id].paste(im, bbox)

        self.action = ("PAST",)
        self.__store()

        return s

    def chunk_BLNK(self, offset, bytes):
        "BLNK -- create blank image"

        # assertions
        if self.count == 0:
            raise SyntaxError, "misplaced BLNK chunk"

        s = self.fp.read(bytes)
        size, mode, rawmode = self.__getmodesize(s, 0)

        # store image (FIXME: handle colour)
        self.action = ("BLNK",)
        self.im = Image.core.fill(mode, size, 0)
        self.__store()

        return s

    def chunk_IHDR(self, offset, bytes):
        "IHDR -- full image follows"

        # assertions
        if self.count == 0:
            raise SyntaxError, "misplaced IHDR chunk"

        # image header
        s = self.fp.read(bytes)
        size, mode, rawmode = self.__getmodesize(s)

        # decode and store image
        self.action = ("IHDR",)
        self.im = Image.core.new(mode, size)
        self.decoder = Image.core.zip_decoder(rawmode)
        self.decoder.setimage(self.im, (0,0) + size)
        self.data = ""

        return s

    def chunk_DHDR(self, offset, bytes):
        "DHDR -- delta image follows"

        # assertions
        if self.count == 0:
            raise SyntaxError, "misplaced DHDR chunk"

        s = self.fp.read(bytes)

        size, mode, rawmode = self.__getmodesize(s)

        # delta header
        diff = ord(s[13])
        offs = i32(s[14:18]), i32(s[18:22])

        bbox = offs + (offs[0]+size[0], offs[1]+size[1])

        if Image.DEBUG:
            print "DHDR", diff, bbox

        # FIXME: decode and apply image
        self.action = ("DHDR", diff, bbox)

        # setup decoder
        self.im = Image.core.new(mode, size)

        self.decoder = Image.core.zip_decoder(rawmode)
        self.decoder.setimage(self.im, (0,0) + size)

        self.data = ""

        return s

    def chunk_JHDR(self, offset, bytes):
        "JHDR -- JPEG image follows"

        # assertions
        if self.count == 0:
            raise SyntaxError, "misplaced JHDR chunk"

        # image header
        s = self.fp.read(bytes)
        size, mode, rawmode = self.__getmodesize(s, 0)

        # decode and store image
        self.action = ("JHDR",)
        self.im = Image.core.new(mode, size)
        self.decoder = Image.core.jpeg_decoder(rawmode)
        self.decoder.setimage(self.im, (0,0) + size)
        self.data = ""

        return s

    def chunk_UHDR(self, offset, bytes):
        "UHDR -- uncompressed image data follows (EXPERIMENTAL)"

        # assertions
        if self.count == 0:
            raise SyntaxError, "misplaced UHDR chunk"

        # image header
        s = self.fp.read(bytes)
        size, mode, rawmode = self.__getmodesize(s, 0)

        # decode and store image
        self.action = ("UHDR",)
        self.im = Image.core.new(mode, size)
        self.decoder = Image.core.raw_decoder(rawmode)
        self.decoder.setimage(self.im, (0,0) + size)
        self.data = ""

        return s

    def chunk_IDAT(self, offset, bytes):
        "IDAT -- image data block"

        # pass compressed chunks through the decoder
        s = self.fp.read(bytes)
        self.data = self.data + s
        n, e = self.decoder.decode(self.data)
        if n < 0:
            # end of image
            if e < 0:
                raise IOError, "decoder error %d" % e
        else:
            self.data = self.data[n:]

        return s

    def chunk_DEND(self, offset, bytes):
        return self.chunk_IEND(offset, bytes)

    def chunk_JEND(self, offset, bytes):
        return self.chunk_IEND(offset, bytes)

    def chunk_UEND(self, offset, bytes):
        return self.chunk_IEND(offset, bytes)

    def chunk_IEND(self, offset, bytes):
        "IEND -- end of image"

        # we now have a new image.  carry out the operation
        # defined by the image header.

        # won't need these anymore
        del self.decoder
        del self.data

        self.__store()

        return self.fp.read(bytes)

    def __store(self):

        # apply operation
        cid = self.action[0]

        if cid in ["BLNK", "IHDR", "JHDR", "UHDR"]:
            # store
            self.images[self.id] = self.im

        elif cid == "DHDR":
            # paste
            cid, mode, bbox = self.action
            im0 = self.images[self.id]
            im1 = self.im
            if mode == 0:
                im1 = im1.chop_add_modulo(im0.crop(bbox))
            im0.paste(im1, bbox)

        self.count = self.count - 1

        if self.count == 0 and self.show:
            self.im = self.images[self.id]
            raise EOFError # end of this frame

    def chunk_PLTE(self, offset, bytes):
        "PLTE -- palette data"

        s = self.fp.read(bytes)
        if self.mode == "P":
            self.palette = ImagePalette.raw("RGB", s)
        return s

    def chunk_sYNC(self, offset, bytes):
        "SYNC -- reset decoder"

        if self.count != 0:
            raise SyntaxError, "misplaced sYNC chunk"

        s = self.fp.read(bytes)
        self.__reset()
        return s

    #
    # LEVEL 2 STUFF

    def chunk_aAPP(self, offset, bytes):
        "aAPP -- store application"

        s = self.fp.read(bytes)

        # extract type, name and code chunk
        j = string.find(s, "\0")
        name = s[:j]

        i = j + 1
        j = string.find(s, "\0", i)
        type = s[i:j]

        code = s[j+1:]

        if Image.DEBUG:
            print "AAPP", repr(type), repr(name)

        if not code:
            # delete existing applet
            if self.applets.has_key(name):
                del self.applets[name]
        else:
            # store or execute applet
            if type != "python":
                raise IOError, "unsupported script type " + type
            # convert to executable object
            code = marshal.loads(code)
            if not name:
                # unnamed; execute immediately
                self.__applet(code)
            else:
                try:
                    # named applet; store in dictionary
                    self.applets[name] = marshal.loads(code)
                except:
                    pass # applet loading error

        return s

    def chunk_aRUN(self, offset, bytes):
        "aRUN -- execute application"

        s = self.fp.read(bytes)

        j = string.find(s, "\0")
        name = s[:j]

        # FIXME: should handle arguments
        print "ARUN", name

        self.__applet(self.applets[name])

        return s

    def __applet(self, code):

        if not APPLET_HOOK:
            return

        # run script in safe environment
        safe = rexec.RExec()
        safe.r_exec(code)

        # must convert images to Image object form
        images = {}
        for id, im in self.images.items():
            # FIXME: this is crude: support for this operation
            # should be moved to the Image module itself (or
            # better; change this module to use Image objects
            # instead of core objects)
            i = Image.new(im.mode, im.size)
            i.im = im
            images[id] = i
            if self.names.has_key(id):
                # add named image
                images[self.names[id]] = i

        APPLET_HOOK(safe.modules["__main__"].Animation, images)


# --------------------------------------------------------------------
# ARG reader

def _accept(prefix):
    return prefix[:8] == MAGIC

##
# Image plugin for the experimental Animate Raster Graphics format.

class ArgImageFile(ImageFile.ImageFile):

    format = "ARG"
    format_description = "Animated raster graphics"

    def _open(self):

        if self.fp.read(8) != MAGIC:
            raise SyntaxError, "not an ARG file"

        self.arg = ArgStream(self.fp)

        # read and process the first chunk (AHDR)

        cid, offset, bytes = self.arg.read()

        if cid != "AHDR":
            raise SyntaxError, "expected an AHDR chunk"

        s = self.arg.call(cid, offset, bytes)

        self.arg.crc(cid, s)

        # image characteristics
        self.mode = self.arg.mode
        self.size = self.arg.size

    def load(self):

        if self.arg.im is None:
            self.seek(0)

        # image data
        self.im = self.arg.im
        self.palette = self.arg.palette

        # set things up for further processing
        Image.Image.load(self)

    def seek(self, frame):

        if self.arg.eof:
            raise EOFError, "end of animation"

        self.fp = self.arg.fp

        while 1:

            #
            # process chunks

            cid, offset, bytes = self.arg.read()

            if self.arg.eof:
                raise EOFError, "end of animation"

            try:
                s = self.arg.call(cid, offset, bytes)
            except EOFError:
                break

            except "glurk": # AttributeError
                if Image.DEBUG:
                    print cid, bytes, "(unknown)"
                s = self.fp.read(bytes)

            self.arg.crc(cid, s)

        self.fp.read(4) # ship extra CRC

    def tell(self):
        return 0

    def verify(self):
        "Verify ARG file"

        # back up to first chunk
        self.fp.seek(8)

        self.arg.verify(self)
        self.arg.close()

        self.fp = None

#
# --------------------------------------------------------------------

Image.register_open("ARG", ArgImageFile, _accept)

Image.register_extension("ARG", ".arg")

Image.register_mime("ARG", "video/x-arg")
