import os
supportdir = os.path.dirname(os.path.abspath(__file__))
moduledir = supportdir + '/../usr/share/'

import sys
sys.path.append(moduledir)

from ipseity import *

db_helpers.init_db()
app.run(debug=True, host='0.0.0.0')
