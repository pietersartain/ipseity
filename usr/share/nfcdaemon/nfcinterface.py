from py532lib.i2c import *
from py532lib.frame import *
from py532lib.constants import *
from dbinterface import DBInterface
import sqlite3
import logging

import RPi.GPIO as GPIO

import binprint

class NFCInterface:
  def __init__(self, logger=None):
    # Member variables
    self.running = False
    self.writing = False
    self.write_data = [0] # 16bytes
    self.nfc = Pn532_i2c()
    self.db = None
    self.logger = logger or logging.getLogger(__name__)

    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(12,GPIO.OUT, initial=0) # Red
    GPIO.setup(15,GPIO.OUT, initial=0) # Green
    # GPIO.cleanup()

    # Initiate the PN532 module

    self.logger.info('Initializing PN532 ...')
    # Send a FirmwareVersion command
    frame = Pn532Frame(frame_type=PN532_FRAME_TYPE_DATA, data=bytearray([PN532_COMMAND_GETFIRMWAREVERSION]))
    self.nfc.send_command_check_ack(frame)
    response = self.nfc.read_response()

    # Ensure the SAM (Security Access Module) is basically off
    self.nfc.SAMconfigure()

  def red(self, state):
    GPIO.output(12,state)

  def green(self, state):
    GPIO.output(15,state)

  def blink(self, id, number, initial=0):
    for x in range(0,number):
      GPIO.output(id, initial)
      sleep(0.2)
      GPIO.output(id, not initial)
      sleep(0.2)

  def start(self):
    self.logger.info('Starting NFCInterface ...')
    self.db = DBInterface(self.logger)
    self.running = True
    while (self.running):
      # Block waiting for a swipe
      uuid = self.get_uuid()

      # What we really want here is a callback interface, to abstract away the 
      # specifics of this particular project. For now, we make it work. 

      if (self.writing):
        # If we're in writing mode
        self.logger.info('In writing mode')
        success = 1

        # Populate the database with the UUID, if it's not already available,
        #  so at least this card is registered.
        card_id = self.db.register_card(uuid)
        if card_id is None:
          success = 0

        # Authenticate for reading/writing
        self.mifare_auth(uuid, 0x04)
        ids = [self.write_data[0], card_id, 0,0,
               0,0,0,0,  0,0,0,0,  0,0,0,0]
        self.mifare_write(0x04, ids)

        self.mifare_auth(uuid, 0x05)
        md5hash = self.write_data[2:]
        self.mifare_write(0x05, md5hash)

        #binprint.print_r_t(self.write_data, "Data to be written")

        # Need a check here to determine if the card has written correctly,
        # then we can trust the success check below.

        if (success):
          self.db.update_card(card_id, self.write_data[0])
          self.writing = False
          self.logger.info('Success beep.')
          self.red(0)
          self.blink(15,3,0)

        else:
          self.logger.info("Failure beep.")
          self.green(0)
          self.blink(12,3,0)
  
      else:
        # If we're not in writing mode, we're in default reading mode
        self.mifare_auth(uuid, 0x04)
        response_A = self.mifare_read(0x04)

        self.mifare_auth(uuid, 0x04)
        response_B = self.mifare_read(0x05)

        user_id = self.db.check_hash(uuid, response_A, response_B)
        if (user_id):
          logged_in = self.db.toggle_status(user_id) # 1 in, 0 out
          if (logged_in):
            self.logger.info("Success in beep.")
            self.green(1)
          else:
            self.logger.info("Success out beep.")
            self.blink(15,2,1)
        else:
          self.logger.info("Failure beep.")
          self.red(1)

      sleep(0.5)
      self.logger.info("LED reset")
      self.green(0)
      self.red(0)

      # Delay the loop reset for a bit of time
      # to prevent someone from leaning on the
      # login/logout button.
      sleep(3)

  def stop(self):
    self.logger.info('Stopping NFCInterface ...')
    self.running = False
    self.nfc.stop()

  def set_writing(self, write_data):
    self.logger.info('Received data to write')
    self.red(1)
    self.green(1)
    #binprint.print_r_t(write_data, "Received: ")
    self.writing = True
    self.write_data = write_data

  def get_uuid(self):
    uuid_frame = self.nfc.read_mifare()
    if uuid_frame is None:
      return
    else:
      return uuid_frame.get_data()[-4:]

  def mifare_auth(self, uuid, block):
    if uuid is None:
      return
    # Apparently, before we can do anything at all, we must authenticate against the block.
    # Arduino calls MifareAuthenticate, which wraps the command PN532_COMMAND_INDATAEXCHANGE
    # (0x40) issued to pn532 with payload MIFARE_CMD_AUTH_A (0x60) on block.
    auth_data =  bytearray([0x40,0x01,0x60,block]) # PN532 + MiFare command
    auth_data += bytearray([0xff,0xff,0xff,0xff,0xff,0xff]) # default auth KeyA
    auth_data += uuid
    frame = Pn532Frame(frame_type=PN532_FRAME_TYPE_DATA, data=auth_data)
    self.nfc.send_command_check_ack(frame)

  def mifare_read(self, block):
    # Let's try and read a particular block, shall we?
    # So, the Arduino code uses MifareReadBlock, which is a wrapper around the command
    # PN532_COMMAND_INDATAEXCHANGE (0x40) issued to the pn532 controller logical relevant
    # target 0x01, with the payload of MIFARE_CMD_READ (0x30) on block.
    # Build the frame
    frame = Pn532Frame(frame_type=PN532_FRAME_TYPE_DATA, data=bytearray([0x40,0x01,0x30,block]))
    # Issue the command
    self.nfc.send_command_check_ack(frame)
    response = self.nfc.read_response()
    return response.get_data()

  def mifare_write(self, block, data):
    # Write write write! What a risk.
    # Arduino uses MifareWriteBlock; a wrapper around PN532_COMMAND_INDATAEXCHANGE (0x40)
    # issued to pn532, logical relevant target 0x01, with a payload of MIFARE_CMD_WRITE
    # (0xA0) on block.
    # Then you've got 16 bytes you can fill with stuff and/or things.
    write_data =  bytearray([0x40,0x01,0xA0,block])
    write_data += bytearray(data)
    frame = Pn532Frame(frame_type=PN532_FRAME_TYPE_DATA, data=write_data)
    self.nfc.send_command_check_ack(frame)
