from ipseity import app
import sqlite3
from flask import g

DATABASE = '/var/ipseity.db'

def init_db():
  with app.app_context():
    db = get_db()
    with app.open_resource('setup/setup.sql',mode='r') as f:
      db.cursor().executescript(f.read())
    db.commit()

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
      g._database = sqlite3.connect(DATABASE)
      g._database.row_factory = sqlite3.Row
      db = g._database
    return db

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

def run_db(query, args=()):
    cur = get_db().execute(query, args)
    rowid = cur.lastrowid
    get_db().commit()
    cur.close()
    return rowid

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()
