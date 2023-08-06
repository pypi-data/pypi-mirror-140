import socket, threading
from _thread import *

class Server:
    def __init__(self, port):
        self.port = port
        self.server = socket.socket()
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind(((socket.gethostname()), port))
        self.clients = []
        self.addresses = []
        listen = threading.Thread(target=self.listening)
        listen.start()
        send = threading.Thread(target=self.sender)
        send.start()

    def listening(self):
        while True:
            self.server.listen()
            self.conn, self.addr = self.server.accept()
            start_new_thread(self.listener, ())

    def listener(self):
        while True:
            try:
                self.clients.index(self.conn)
            except:
                self.clients.append(self.conn)
                self.addresses.append(self.addr)
            receive = self.conn.recv(4096)
            print(f'\n{self.addr} -=> {receive.decode()}')

    def sender(self):
        while True:
            self.message = input('Text to send <-> ')
            start_new_thread(self.sendMsg, ())

    def sendMsg(self):
        for conn in self.clients:
            conn.send((self.message).encode())

class Client:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.client = socket.socket()
        self.client.connect((self.host, self.port))
        self.client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listen = threading.Thread(target=self.listener)
        listen.start()
        send = threading.Thread(target=self.sender)
        send.start()

    def listener(self):
        while True:
            received = self.client.recv(4096)
            print(f'\nFrom server -=> {received.decode()}')

    def sender(self):
        while True:
            self.message = input('Text to send <-> ')
            start_new_thread(self.sendMsg, ())

    def sendMsg(self):
        self.client.send((self.message).encode())