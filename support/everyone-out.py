import os
supportdir = os.path.dirname(os.path.abspath(__file__))
moduledir = supportdir + '/../usr/share/'

import sys
sys.path.append(moduledir)

from ipseity import *

app = Flask(__name__)
with app.app_context():
  db_helpers.init_db()

  # This should return all the people currently logged in.
  people_list = db_helpers.query_db("SELECT * FROM users WHERE logged_in = 1;")

  for person in people_list:
    people.toggle_logged_in_state(person['user_id'])
