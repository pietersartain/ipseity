from ipseity import app
from flask import render_template, request, url_for, redirect, send_file, make_response
from ipseity import db_helpers, people
import sqlite3 # Binary
import socket
import traceback
import hashlib
import time
import calendar

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
  times = parse_times(s_from, s_to)
  t_from = times[0]
  t_to = times[1]
  events = get_events(t_from, t_to)

  # Convert events array into:
  #   per-person in, out, durations, number of visits, average duration
  people_list = dict()
  #   total duration in use, number of individual visits
  #   average duration, average visits per user
  overview_stats = {'duration':0, 'visits':0, 'av_duration_per_user':0, 'av_visits_per_user':0}
  #   time heat map of visits (or graph of usage by body count)
  #   most popular times, least popular times

  last_in = 0
  last_out = 0

  for event in events:
    if (event['name'] not in people_list):
      people_list[event['name']] = {'in':0, 'out':0, 'duration':0, 'visits':0, 'average_duration':0}

    if (event['logged_in'] == 1):
      people_list[event['name']]['in'] += 1
      last_in = event['event_when']

    if (event['logged_in'] == 0):
      people_list[event['name']]['out'] += 1
      last_out = event['event_when']
      if (last_in == 0):
        last_in = int(t_from)

      duration = last_out - last_in

      if (duration > 0):
        #
        people_list[event['name']]['duration'] += duration
        people_list[event['name']]['visits'] += 1
        people_list[event['name']]['average_duration'] = people_list[event['name']]['duration'] / people_list[event['name']]['visits']
        #
        overview_stats['duration'] += duration
        overview_stats['visits'] += 1
        #

  overview_stats['av_visits_per_user'] = overview_stats['visits'] / len(people_list)
  overview_stats['av_duration_per_user'] = overview_stats['duration'] / len(people_list)

  return render_template('report.jhtml', people=people_list, overview=overview_stats)

# From/To are YYYYMMDD formatted strings
@app.route("/report/csv/<s_from>/<s_to>")
def report_csv(s_from, s_to):

  times = parse_times(s_from, s_to)
  t_from = times[0]
  t_to = times[1]
  events = get_events(t_from, t_to)

#  s_from = time.strptime(t_from, "%s")
#  s_to   = time.strptime(t_to,   "%s")

  file_name = '/tmp/%s_%s.csv' % (t_from, t_to)
  f = open(file_name,'w')
  for event in events:
    f.write(event['line'] + "\n")
  f.close()

  return send_file(file_name, as_attachment=True)

def parse_times(s_from, s_to):
  ltime = time.localtime()

  # If the from or to times are set to 0,
  # treat them as if they were last month.
  if (s_from == "0"):
    s_from = '%s%s01' % (ltime[0], ltime[1]-1)

  if (s_to == "0"):
    monthrange = calendar.monthrange(ltime[0], ltime[1]-1)
    s_to = '%s%s%s' % (ltime[0], ltime[1]-1, monthrange[1])

  t_from = time.strftime('%s', time.strptime(s_from, "%Y%m%d"))
  t_to   = time.strftime('%s', time.strptime(s_to,   "%Y%m%d"))

  return (t_from, t_to)

def get_events(t_from, t_to):
  # ltime = time.localtime()
  # monthrange = calendar.monthrange(ltime[0], ltime[1])

  # if (s_from == "0"):
  #   s_from = '%s%s01' % (ltime[0], ltime[1])

  # if (s_to == "0"):
  #   s_to = '%s%s%s' % (ltime[0], ltime[1], monthrange[1])

  # s_from = time.strftime('%s', time.strptime(s_from, "%Y%m%d"))
  # s_to   = time.strftime('%s', time.strptime(s_to,   "%Y%m%d"))

  events = db_helpers.query_db("""
    SELECT u.name || ',' || a.event_when || ',' || a.logged_in AS line,
    u.name AS name, a.event_when AS event_when, a.logged_in AS logged_in
    FROM attendance AS a 
    JOIN users AS u 
    ON u.user_id = a.user_id
    WHERE event_when BETWEEN ? AND ?
    ORDER BY name ASC, event_when ASC
    """, (t_from, t_to))

# """
#     SELECT u.name || ',' || a.event_when || ',' || a.logged_in AS line,
#     u.name AS name, a.event_when AS event_when, a.logged_in AS logged_in
#     FROM attendance AS a 
#     JOIN users AS u 
#     ON u.user_id = a.user_id
#     WHERE event_when BETWEEN 1377993600 AND 1380499200
#     ORDER BY name asc, event_when asc
# """

  return events

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
  db_helpers.run_db('delete from attendance where user_id = ?',(user_id,) )
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
