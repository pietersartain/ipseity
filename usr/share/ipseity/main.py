from ipseity import app
from flask import render_template, request, url_for, redirect, send_file, make_response
from ipseity import db_helpers, people
import sqlite3 # Binary
import socket
import traceback
import hashlib

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Support functions
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Convenience function for the view side of things
def get_people(logged_in = None):

  if (logged_in == 1):
    people_list = people.get_in()

  if (logged_in == 0):
    people_list = people.get_out()

  if (logged_in == None):
    people_list = people.get_all()

  if (request.args.get('ajax')):
    return render_template('peoplelist.jhtml', people=people_list)
  else:
    return render_template('people.jhtml', people=people_list)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Main view routes
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# We have 3 different types of views atm, but / isn't one of them.
@app.route("/")
def title():
  return redirect('/people/all')

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# People views
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Show all of the people
@app.route("/people/all")
def people_all():
  return get_people()

# Show only the people who are currently logged in
@app.route("/people/in")
def people_in():
  return get_people(1)

# Show only the people who are currently logged out
@app.route("/people/out")
def people_out():
  return get_people(0)

# Show all of the people
@app.route("/people/edit")
def people_edit():
  people_list = people.get_full_people()
  return render_template('editpeople.jhtml', people=people_list)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Report views
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

@app.route("/report/overview/<s_from>/<s_to>")
def report_overview(s_from, s_to):
# "SELECT col_b as clock_in, col_a as clock_out, strftime('%s', col_a)-strftime('%s', col_b) \
#   FROM (  \
#   SELECT q.user_id as user_id, q.event_when as col_a, \
#     coalesce((select r.event_when from attendance as r \
#                         where r.user_id = q.user_id \
#                         and r.event_when < q.event_when \
#                         order by r.event_when DESC limit 1), \
#                         q.event_when) as col_b \
#     FROM attendance as q WHERE q.user_id NOT NULL \
#     ORDER BY q.user_id ASC, q.event_when ASC );"
  #events = db_helpers.query_db("select event_when, u.name from attendance as a join users as u on u.user_id = a.user_id between ... and ...")

  # Convert events array into:
  #   per-person in, out, durations, number of visits, average duration
  #   total duration in use, number of individual visits
  #   average duration, average visits per user
  #   most popular times, least popular times
  #   time heat map of visits (or graph of usage by body count)
  return ""

# @app.route("/report/csv/<str:s_from>/<str:s_to>")
# def report_csv(s_from, s_to):
# SELECT u.name, a.logged_in, a.event_when, strftime('%s',event_when)
# FROM attendance as a 
# join users as u on u.user_id = a.user_id
# WHERE a.event_when BETWEEN '2013-09-27 20:33:46' and '2013-09-27 20:33:49'
# order by a.user_id desc, a.event_when asc;

#AND strftime('%s', a.event_when) < strftime('%s','now')


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# People helper functions
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# User-supplied image, to be called in <img src='' />
@app.route("/people/<int:user_id>/img")
def get_image(user_id):
  user_info = db_helpers.query_db('select image from users where user_id = ?', [user_id], one=True)
  img = str(user_info['image'])
  response = make_response(img)
  response.headers['Content-Type'] = 'image/jpeg'
  return response

# Add a new person to the DB
@app.route("/people/new", methods=['POST'])
def add_person():
  name = request.form.get('name')
  img  = sqlite3.Binary(request.files.get('img').read())
  db_helpers.run_db('insert into users(name, image) values(?,?)',(name, img) )
  return redirect('/people/edit')

# Completely remove a person, including all of their cards, from the DB
@app.route("/people/<int:user_id>/delete")
def remove_person(user_id):
  db_helpers.run_db('delete from cards where user_id = ?',(user_id,) )
  db_helpers.run_db('delete from users where user_id = ?',(user_id,) )
  return redirect('/people/edit')

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Card helper functions
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Link a card to a person via the nfcdaemon UD socket
@app.route("/people/<int:user_id>/link")
def trigger_link(user_id):
  user_info = db_helpers.query_db("SELECT * FROM users WHERE user_id = ?", (user_id,), True)
  hash_str = str("spamspam" + str(user_info["user_id"]) + user_info["name"]).encode("utf-8")
  m = hashlib.md5(hash_str)
  user_hash  = bytearray( (user_info["user_id"], 0) )
  user_hash += bytearray(m.digest())

  server_address = '/tmp/nfcdaemon'
  sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
  message = ''
  try:
    sock.connect(server_address)
    message = bytearray('write ') + user_hash
    sock.sendall( message )
  except:
    message = traceback.format_exc()
  finally:
    sock.close()
  return redirect('/people/edit')

# Remove a card/person association
@app.route("/cards/<int:card_id>/delete")
def remove_card(card_id):
  db_helpers.run_db('delete from cards where card_id = ?',(card_id,) )
  return redirect('/people/edit')

if __name__ == '__main__':
    app.run()
