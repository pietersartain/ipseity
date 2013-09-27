from ipseity import app
from flask import render_template, request, url_for, redirect, send_file, make_response
from ipseity import db_helpers
import sqlite3 # Binary
import socket
import traceback
import hashlib

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Support functions
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Fill out a list of people with their card details, ready for
# sending to the view.
# This could mostly be done with a single SQL, but it's more hard work
# than it needs to be, and this is plenty efficient enough for now.
def get_full_people(user_records):
  people_list = []

  for user_record in user_records:
    person_record = dict()
    # person_record['details'] = user_record

    card_records = db_helpers.query_db('select * from cards where user_id = ?',
      (user_record['user_id'],) )

    card_list = []
    for card_record in card_records:
      card_r = dict()
      card_r['card_uuid'] = str(card_record['card_uuid']).encode('hex')
      card_r['card_id'] = card_record['card_id']
      card_list.append(card_r)

    if ( len(str(user_record['image'])) > 0 ):
      image_url = '/people/' + str(user_record['user_id']) + '/img'
    else:
      image_url = url_for('static', filename='img/icon-black.png')
    
    person_record = { \
      'cards':card_list, \
      'user_id':user_record['user_id'], \
      'image_url':image_url, \
      'name':user_record['name'], \
      # 'cardcount':card_records['count'], \
      'logged_in': (True if (user_record['logged_in'] == 1) else False) }

    people_list.append(person_record)
  return people_list

# Now this function really does need optimising. omgooses.
def get_people(sql):
  user_records = db_helpers.query_db(sql)

  people_list = []
  for user_record in user_records:
    person_record = dict()

    if ( len(str(user_record['image'])) > 0 ):
      image_url = '/people/' + str(user_record['user_id']) + '/img'
    else:
      image_url = url_for('static', filename='img/icon-black.png')

    card_records = db_helpers.query_db('select count(*) as count from cards where user_id = ?',
      (user_record['user_id'],), True )
    
    person_record = { \
      'user_id':user_record['user_id'], \
      'image_url':image_url, \
      'name':user_record['name'], \
      'cardcount':card_records['count'], \
      'logged_in': (True if (user_record['logged_in'] == 1) else False) }

    people_list.append(person_record)

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
  return get_people('select * from users')

# Show only the people who are currently logged in
@app.route("/people/in")
def people_in():
  return get_people('select * from users where logged_in = 1')

# Show only the people who are currently logged out
@app.route("/people/out")
def people_out():
  return get_people('select * from users where logged_in = 0')

# Show all of the people
@app.route("/people/edit")
def people_edit():
  user_records = db_helpers.query_db('select * from users')
  people = get_full_people(user_records)
  return render_template('editpeople.jhtml', people=people)


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
