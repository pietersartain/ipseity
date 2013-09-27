import sys
import signal
import os
import socket
import traceback
import logging

from dbinterface import DBInterface

import binprint

# def signal_handler(signal, frame):
#   sys.exit(0)
# signal.signal(signal.SIGINT, signal_handler)

class NFCClient:
  def __init__(self, server_address, logger=None):
    # Member variables
    self.running = True
    self.server_address = server_address
    self.db = DBInterface()
    self.logger = logger or logging.getLogger(__name__)

  def send(self, message):
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    try:
      sock.connect(self.server_address)

      message = bytearray(message.encode("utf-8"))

      if (message == b'write'):
        message += bytearray(b' ') + db.hash_user(1,1)

      # Send data
      #binprint.print_r_t( message, "Sending: ")

      sock.sendall( message )

    except:
      self.logger.info("Ouch. Pop! ")
      self.logger.info(traceback.format_exc())
      #sys.exit(1)

    finally:
      self.logger.info("Yeah, we're done.")
      sock.close()

if __name__ == "__main__":
  nfcclient = NFCClient('/tmp/nfcdaemon')

  message = ''
  while (message != b'quit'):
    message = input("Send to UDS: ")
    nfcclient.send(message)

