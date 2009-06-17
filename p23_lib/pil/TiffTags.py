#
# The Python Imaging Library.
# $Id: //modules/pil/PIL/TiffTags.py#2 $
#
# TIFF tags
#
# This module provides clear-text names for various well-known
# TIFF tags.  the TIFF codec works just fine without it.
#
# Copyright (c) Secret Labs AB 1999.
#
# See the README file for information on usage and redistribution.
#

TAGS = {

    254: "NewSubfileType",
    255: "SubfileType",
    256: "ImageWidth",
    257: "ImageLength",
    258: "BitsPerSample",

    259: "Compression",
    (259, 1): "uncompressed",
    (259, 2): "ccitt 1d",
    (259, 3): "group 3 fax",
    (259, 4): "group 4 fax",
    (259, 5): "lzw",
    (259, 6): "jpeg",
    (259, 32773): "packbits",

    262: "PhotometricInterpretation",
    (262, 0): "whiteiszero",
    (262, 1): "blackiszero",
    (262, 2): "rgb",
    (262, 3): "rgb palette",
    (262, 4): "transparency mask",
    (262, 5): "cmyk",
    (262, 6): "ycbcr",
    (262, 8): "cielab",

    263: "Thresholding",
    264: "CellWidth",
    265: "CellHeight",
    266: "FillOrder",
    269: "DocumentName",

    270: "ImageDescription",
    271: "Make",
    272: "Model",
    273: "StripOffsets",
    274: "Orientation",
    277: "SamplesPerPixel",
    278: "RowsPerStrip",
    279: "StripByteCounts",

    280: "MinSampleValue",
    281: "MaxSampleValue",
    282: "XResolution",
    283: "YResolution",
    284: "PlanarConfiguration",
    (284, 1): "contigous",
    (284, 2): "separate",

    285: "PageName",
    286: "XPosition",
    287: "YPosition",
    288: "FreeOffsets",
    289: "FreeByteCounts",

    290: "GrayResponseUnit",
    291: "GrayResponseCurve",
    292: "T4Options",
    293: "T6Options",
    296: "ResolutionUnit",
    297: "PageNumber",

    301: "TransferFunction",
    305: "Software",
    306: "DateTime",

    315: "Artist",
    316: "HostComputer",
    317: "Predictor",
    318: "WhitePoint",
    319: "PrimaryChromaticies",

    320: "ColorMap",
    321: "HalftoneHints",
    322: "TileWidth",
    323: "TileLength",
    324: "TileOffsets",
    325: "TileByteCounts",

    332: "InkSet",
    333: "InkNames",
    334: "NumberOfInks",
    336: "DotRange",
    337: "TargetPrinter",
    338: "ExtraSamples",
    339: "SampleFormat",

    340: "SMinSampleValue",
    341: "SMaxSampleValue",
    342: "TransferRange",

    347: "JPEGTables",

    # obsolete JPEG tags
    512: "JPEGProc",
    513: "JPEGInterchangeFormat",
    514: "JPEGInterchangeFormatLength",
    515: "JPEGRestartInterval",
    517: "JPEGLosslessPredictors",
    518: "JPEGPointTransforms",
    519: "JPEGQTables",
    520: "JPEGDCTables",
    521: "JPEGACTables",

    529: "YCbCrCoefficients",
    530: "YCbCrSubSampling",
    531: "YCbCrPositioning",
    532: "ReferenceBlackWhite",

    33432: "Copyright",

    # various extensions (should check specs for "official" names)
    33723: "IptcNaaInfo",
    34377: "PhotoshopInfo",

}

TYPES = {

    1: "byte",
    2: "ascii",
    3: "short",
    4: "long",
    5: "rational",
    6: "signed byte",
    7: "undefined",
    8: "signed short",
    9: "signed long",
    10: "signed rational",
    11: "float",
    12: "double",

}
