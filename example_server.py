#!/usr/bin/python

import socket
import select
import sys
import time
import xml.etree.ElementTree as ET
from rospkg import RosPack
from threading import Thread, Lock
from copy import deepcopy
""" Setting up a server to TCP/IP comm testing """


class TestServer(object):
  """ Setup the basics of the server """

  def __init__(self):
    self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # This populates with the the IP and port, lookup what port to use.
    # ex: self.server_address = ("192.168.1.100", 22171)
    self.server_address = ('localhost', 22171)
    self._lock = Lock()
    self._data = []

  """ Start the server comm on localhost """

  def run(self):
    print(sys.stderr, "starting server up on %s with port %s" % self.server_address)
    # set to reconnect to avoid timeout issues
    self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    self.sock.bind(self.server_address)
    self.connected = False
    self.sock.listen(1)

    while not self.connected:
      # wait for the connection
      print(sys.stdout, 'waiting for connection')
      self.connection, self.client_address = self.sock.accept()
      time.sleep(0.5)
      if self.connection:
        self.connected = True

    print(sys.stdout, ' found connection from ', self.client_address)

    # spin up reading thread
    self._data_thread = Thread(target=self._run_data_thread)
    self._data_thread.daemon = True
    self._data_thread.start()

    while self.connected:
      # set the lock to read the current common variable
      # lock will release with with statement ends
      with self._lock:
        print("Current data in buffer is {}".format(self._data))
      time.sleep(1/10.0)

  def _run_data_thread(self):
    print("data thread starting")
    while self.connected:
      data = ''
      # check for data on the buffer
      ready = select.select([self.connection], [], [], 0.01)
      # if data on the buffer, read it
      if ready[0]:
        data = self.connection.recv(1024)
      if data:
        print(sys.stdout, 'received %s' % data)
        # return a copy to the user of what they sent
        self.connection.sendall(deepcopy(data))
        # set the lock to manipulate the common variable
        # when the with section ends, the lock is released
        with self._lock:
          self._data.append(data)
        data = ''
      else:
        pass
      time.sleep(0.01)





if __name__ == "__main__":
  server = TestServer()
  server.run()
