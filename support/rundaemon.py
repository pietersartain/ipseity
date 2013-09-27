import os
supportdir = os.path.dirname(os.path.abspath(__file__))
moduledir = supportdir + '/../usr/share/'

import sys
sys.path.append(moduledir)

import nfcdaemon

nfcdaemon.main()
