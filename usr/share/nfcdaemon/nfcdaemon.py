import sys
import time
import signal
import threading
import logging

from nfcinterface import NFCInterface
from nfcsocket import NFCSocket
#from ledinterface import LEDInterface
from nfcclient import NFCClient
from daemon3x import Daemon

logging.basicConfig(level=logging.INFO)

class NFCDaemon(Daemon):
  def __init__(self, pidfile):
    super( NFCDaemon, self ).__init__(pidfile)

    # Logging 
    self.logger = logging.getLogger(__name__)
    self.logger.setLevel(logging.INFO)
    # handler = logging.FileHandler('hello.log')
    # handler.setLevel(logging.INFO)
    # self.logger.addHandler(handler)

    self.nfc = NFCInterface(self.logger)
    self.nfcsocket = NFCSocket('/tmp/nfcdaemon', self.nfc, self.logger)

  def socket_thread(self):
    self.nfcsocket.start()

  def nfc_thread(self):
    self.nfc.start()

  def run(self):
    # Please don't ask why I have to have whole
    # separate class functions for these object calls,
    # but it don't work if I don't do it like this.
    ta = threading.Thread( target=self.nfc_thread )
    tb = threading.Thread( target=self.socket_thread )

    ta.start()
    tb.start()


if __name__ == "__main__":
  daemon = NFCDaemon('/var/run/nfcdaemon.pid')
  if len(sys.argv) == 2:
    if 'start' == sys.argv[1]:
      daemon.start()
    elif 'stop' == sys.argv[1]:
      daemon.stop()
    elif 'restart' == sys.argv[1]:
      daemon.restart()
    elif 'debug' == sys.argv[1]:
      daemon.run()
    else:
      print("Unknown command")
      sys.exit(2)
    sys.exit(0)
  else:
    print("usage: %s start|stop|restart" % sys.argv[0])
    sys.exit(2)
