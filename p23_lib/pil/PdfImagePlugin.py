#
# The Python Imaging Library.
# $Id: //modules/pil/PIL/PdfImagePlugin.py#3 $
#
# PDF (Acrobat) file handling
#
# History:
#       96-07-16 fl     Created
#       97-01-18 fl     Fixed header
#
# Copyright (c) Secret Labs AB 1997.
# Copyright (c) Fredrik Lundh 1996-97.
#
# See the README file for information on usage and redistribution.
#


__version__ = "0.2"

import Image, ImageFile
import StringIO


#
# --------------------------------------------------------------------

# object ids:
#  1. catalogue
#  2. pages
#  3. image
#  4. page
#  5. page contents

def _obj(fp, obj, **dict):
    fp.write("%d 0 obj\n" % obj)
    if dict:
        fp.write("<<\n")
        for k, v in dict.items():
            if v is not None:
                fp.write("/%s %s\n" % (k, v))
        fp.write(">>\n")

def _endobj(fp):
    fp.write("endobj\n")

def _save(im, fp, filename):

    #
    # make sure image data is available
    im.load()

    xref = [0]*(5+1) # placeholders

    fp.write("%PDF-1.2\n")
    fp.write("% created by PIL PDF driver " + __version__ + "\n")

    #
    # Get image characteristics

    width, height = im.size

    # FIXME: Should replace ASCIIHexDecode with RunLengthDecode (packbits)
    # or LZWDecode (tiff/lzw compression).  Note that PDF 1.2 also supports
    # Flatedecode (zip compression).

    params = None

    if im.mode == "1":
        filter = "/ASCIIHexDecode"
        config = "/DeviceGray", "/ImageB", 1
    elif im.mode == "L":
        filter = "/DctDecode"
        # params = "<< /Predictor 15 /Columns %d >>" % (width-2)
        config = "/DeviceGray", "/ImageB", 8
    elif im.mode == "P":
        filter = "/ASCIIHexDecode"
        config = "/Indexed", "/ImageI", 8
    elif im.mode == "RGB":
        filter = "/DCTDecode"
        config = "/DeviceRGB", "/ImageC", 8
    elif im.mode == "CMYK":
        filter = "/DCTDecode"   
        config = "/DeviceRGB", "/ImageC", 8
    else:
        raise ValueError, "illegal mode"

    colorspace, proc, bits = config

    #
    # catalogue

    xref[1] = fp.tell()
    _obj(fp, 1, Type = "/Catalog",
                Pages = "2 0 R")
    _endobj(fp)

    #
    # pages

    xref[2] = fp.tell()
    _obj(fp, 2, Type = "/Pages",
                Count = 1,
                Kids = "[4 0 R]")
    _endobj(fp)

    #
    # image

    op = StringIO.StringIO()

    if filter == "/ASCIIHexDecode":
        ImageFile._save(im, op, [("hex", (0,0)+im.size, 0, None)])
    elif filter == "/DCTDecode":
        ImageFile._save(im, op, [("jpeg", (0,0)+im.size, 0, im.mode)])
    elif filter == "/FlateDecode":
        ImageFile._save(im, op, [("zip", (0,0)+im.size, 0, im.mode)])
    elif filter == "/RunLengthDecode":
        ImageFile._save(im, op, [("packbits", (0,0)+im.size, 0, im.mode)])
    else:
        raise ValueError, "unsupported PDF filter"

    xref[3] = fp.tell()
    _obj(fp, 3, Type = "/XObject",
                Subtype = "/Image",
                Width = width,
                Height = height,
                Length = len(op.getvalue()),
                Filter = filter,
                BitsPerComponent = bits,
                DecodeParams = params,
                ColorSpace = colorspace)

    fp.write("stream\n")
    fp.write(op.getvalue())
    fp.write("\nendstream\n")

    _endobj(fp)

    #
    # page

    xref[4] = fp.tell()
    fp.write("4 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n"\
             "/Resources <<\n/ProcSet [ /PDF %s ]\n"\
             "/XObject << /image 3 0 R >>\n>>\n"\
             "/MediaBox [ 0 0 %d %d ]\n/Contents 5 0 R\n>>\n" %\
             (proc, width, height))

    #
    # page contents

    op = StringIO.StringIO()

    op.write("q %d 0 0 %d 0 0 cm /image Do Q\n" % (width, height))

    xref[5] = fp.tell()
    _obj(fp, 5, Length = len(op.getvalue()))

    fp.write("stream\n")
    fp.write(op.getvalue())

    _endobj(fp)

    #
    # trailer
    startxref = fp.tell()
    fp.write("xref\n0 %d\n0000000000 65535 f \n" % len(xref))
    for x in xref[1:]:
        fp.write("%010d 00000 n \n" % x)
    fp.write("trailer\n<<\n/Size %d\n/Root 1 0 R\n>>\n" % len(xref))
    fp.write("startxref\n%d\n%%%%EOF\n" % startxref)
    fp.flush()

#
# --------------------------------------------------------------------

Image.register_save("PDF", _save)

Image.register_extension("PDF", ".pdf")

Image.register_mime("PDF", "application/pdf")
