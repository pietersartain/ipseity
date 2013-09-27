import sqlite3
import hashlib
import pprint
import binascii
import re
import sys
import logging

import binprint

class DBInterface:
  def __init__(self, logger=None):
    self.db = sqlite3.connect('/var/ipseity.db')
    self.db.row_factory = sqlite3.Row
    self.logger = logger or logging.getLogger(__name__)

  def query_db(self, query, args=(), one=False):
    cur = self.db.execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

  def run_db(self, query, args=()):
    cur = self.db.execute(query, args)
    rowid = cur.lastrowid
    self.db.commit()
    cur.close()
    return rowid    

  def check_hash(self, uuid, blockA, blockB):
    self.logger.info('Checking hash ...')

    if (len(blockA) != 18):
      return

    if (len(blockB) != 18):
      return

    user_id = blockA[2]
    card_id = blockA[3]

#    binprint.print_r(blockA)
#    binprint.print_r(blockB)

    card_info = self.query_db("SELECT * FROM cards WHERE card_id = ?", (card_id,), True)
    if card_info is None:
      self.logger.info("No card info")
      return

#    print(card_info)
#    print(user_id)
#    print(card_info["user_id"])

    if (user_id != card_info["user_id"]):
      self.logger.info("User mismatch")
      return

    if (uuid != card_info["card_uuid"]):
      self.logger.info("Uuid mismatch")
      return

    user_hash = self.hash_user(user_id, card_info["card_id"])
    blockB[0] = user_id
    blockB[1] = card_id

#    binprint.print_r(user_hash)
#    binprint.print_r(blockB)

    if (user_hash == blockB):
      return True
    else:
      return

  def toggle_status(self, uuid):
    user_info = self.query_db("SELECT user_id FROM cards WHERE card_uuid = ?", (uuid,), True)
    if user_info is not None:
      self.run_db("UPDATE users SET logged_in = 1 - logged_in WHERE user_id = ?", (user_info["user_id"],))
      return True
    else:
      return False

  def update_card(self, card_id, user_id):
    self.run_db("UPDATE cards SET user_id = ? WHERE card_id = ?", (user_id, card_id))

  def register_card(self, uuid):
    card_info = self.query_db("SELECT card_id FROM cards WHERE card_uuid = ?", (uuid,), True)
    if card_info is not None:
      return card_info["card_id"]
    return self.run_db("INSERT INTO cards(card_uuid) VALUES(?)", (uuid,))

  def hash_user(self, user_id, card_id):
    user_info = self.query_db("SELECT * FROM users WHERE user_id = ?", (user_id,), True)
    
    hash_str = str("spamspam" + str(user_info["user_id"]) + user_info["name"]).encode("utf-8")
    m = hashlib.md5(hash_str)

#    binprint.print_r_t(m.digest(),"Hash digest")
#    binprint.print_r_t( (card_id).to_bytes(1, sys.byteorder) , "Card ID")
#    print(card_id)
#    binprint.print_r_t( (user_info["user_id"]).to_bytes(1, sys.byteorder) , "User ID")
#    print(user_info["user_id"])

    user_hash  = bytearray( (user_info["user_id"]).to_bytes(1, sys.byteorder) )
    user_hash += bytearray( (card_id).to_bytes(1, sys.byteorder) )
    user_hash += bytearray(m.digest())
    return user_hash
