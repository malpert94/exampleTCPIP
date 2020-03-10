#!/usr/bin/python

import socket
import select
import sys
import time
from threading import Thread
import xml.etree.ElementTree as ET
from rospkg import RosPack
import itertools as IT
import io
StringIO = io.BytesIO

""" Setting up a client to TCP/IP comm testing """


class TestClient(object):
  """ Setup the basics of the client """

  def __init__(self):
    self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # This populates with the the IP and port, lookup what port to use.
    # ex: self.server_address = ("192.168.1.100", 22171)
    self.server_address = ("localhost", 22171)

  """ Connect and talk at an interval to the server """

  def run(self):

    # connect to the the server
    print(sys.stdout, "connecting to %s on port %s as client" % self.server_address)
    self.sock.connect(self.server_address)

    # startup thread to read any messages back from the server
    self._data_thread = Thread(target=self._run_data_thread)
    self._data_thread.daemon = True   # makes the thread dependant on the parent program, so they die together
    self._data_thread.start()

    # send a message with a certain frequency a certain number of times
    for count in range(0,10):
      # send a message piece
      try:
        message = "HELLO"
        self.sock.sendall(message.encode("ASCII"))
        print("Message of {} sent".format(message))
      except:
        print("error while sending")
      time.sleep(1.0)

    print >> sys.stderr, "closing socket"
    self.sock.close()


  def _run_data_thread(self):
    print("data thread starting")
    while True:
      data = ''
      # check for data on the buffer
      ready = select.select([self.sock], [], [], 0.01)
      # if data on the buffer, read it
      if ready[0]:
        data = self.sock.recv(1024)
      if data:
        print(sys.stdout, 'received %s' % data)
        data = ''
      else:
        pass
      time.sleep(0.01)


if __name__ == "__main__":
  client = TestClient()
  client.run()

