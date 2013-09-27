import os
supportdir = os.path.dirname(os.path.abspath(__file__))
moduledir = supportdir + '/../usr/share/'

import sys
sys.path.append(moduledir)

from ipseity import *
#init_db()

import inspect
import pprint

# all_functions = inspect.getmembers(ipseity)#, inspect.isfunction)
# pprint.pprint(all_functions,None,1,80,2)

pprint.pprint(dir(ipseity),None,1,80,2)

# Initialise the DB
#main.init_db()
db_helpers.init_db()
