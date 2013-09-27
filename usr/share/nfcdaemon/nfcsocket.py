import socket
import sys
import os
import logging

class NFCSocket:
  def __init__(self, server_address, nfc, logger=None):
    # Member variables
    self.running = True
    self.server_address = server_address
    self.nfc = nfc
    self.logger = logger or logging.getLogger(__name__)

  def start(self):
    self.logger.info("Starting NFCSocket ... ")
    self.tidy_socket()

    # Create a UD socket
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

    # Bind the socket to the port
    sock.bind(self.server_address)

    # Listen for incoming connections
    self.logger.info("Now listening ... ")
    sock.listen(1)

    while self.running:
      self.logger.info("Waiting for incoming connection ... ")
      # Wait for a connection (blocking)
      connection, client_address = sock.accept()

      try:
        self.logger.info("Connection accepted")
        while self.running:
          data = connection.recv(64)
          if (data == b'quit'):
            self.running = False
            self.nfc.stop()
          
          if (data[:5] == b'write'):
            self.nfc.set_writing(data[6:24])

          if not data:
            break
          
  #        if data:
  #          print("[%s]" % data)
  #        else:
  #          break

      finally:
        connection.close()

    self.logger.info("Finishing with the socket_thread")
    self.tidy_socket()

  def stop(self):
    self.logger.info('Stopping NFCSocket ...')
    self.running = False

  def tidy_socket(self):
    try:
      os.unlink(self.server_address)
    except OSError:
      if os.path.exists(self.server_address):
        raise