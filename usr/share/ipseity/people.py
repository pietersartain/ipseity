from ipseity import app, db_helpers
from flask import url_for
import time

# This is the People model

def get_all():
  return get_people(get_sql())

def get_in():
  sql = get_sql('WHERE logged_in = 1')
  return get_people(sql)

def get_out():
  sql = get_sql('WHERE logged_in = 0')
  return get_people(sql)

def get_sql(where = ""):
  return "SELECT * FROM users " + where

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
    
    if (time.daylight):
      tz = " " + time.tzname[1]
    else:
      tz = " " + time.tzname[0]

    person_record = { \
      'user_id':user_record['user_id'], \
      'image_url':image_url, \
      'name':user_record['name'], \
      'cardcount':card_records['count'], \
      'logged_in': (True if (user_record['logged_in'] == 1) else False), \
      'event_when': time.strftime('%H:%M %d/%m/%Y', time.localtime(user_record['event_when'])) + tz \
#      'event_when': time.localtime(user_record['event_when'])
#      'event_when': time.tzname[0]
    }

    people_list.append(person_record)
  return people_list

# Fill out a list of people with their card details, ready for
# sending to the view.
# This could mostly be done with a single SQL, but it's more hard work
# than it needs to be, and this is plenty efficient enough for now.
def get_full_people():
  user_records = db_helpers.query_db('select * from users')
  people_list = []

  for user_record in user_records:

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
