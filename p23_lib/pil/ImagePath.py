#
# The Python Imaging Library
# $Id: //modules/pil/PIL/ImagePath.py#4 $
#
# path interface
#
# History:
# 1996-11-04 fl   Created
# 2002-04-14 fl   Added documentation stub class
#
# Copyright (c) Secret Labs AB 1997.
# Copyright (c) Fredrik Lundh 1996.
#
# See the README file for information on usage and redistribution.
#

import Image

##
# Path wrapper.

class Path:

    ##
    # Create a path object.
    #
    # @param xy Sequence.

    def __init__(self, xy):
        pass

    ##
    # Compact path contents.

    def compact(self, distance):
        pass

    ##
    # Get bounding box.

    def getbbox(self):
        pass

    ##
    # Map path through function.

    def map(self, function):
        pass

    ##
    # Convert path to Python list.

    def tolist(self):
        pass

    ##
    # Transform path.

    def transform(self, matrix):
        pass


Path = Image.core.path
