import threading
import socket
import time
import ssl

from .info import SSL_VERSION
from .packet import Packet

class Handler(threading.Thread):
    @classmethod
    def connect(cls, address: tuple, client, reconnect: bool = True):
        self = cls()
        self.address = address
        self.reconnect = reconnect
        self.client = client
        self.running = False
        self.connected = True
        try:
            self.tryConnect()
        except (OSError, ssl.SSLError) as e:
            if self.reconnect:
                pass
            else:
                raise e
        return self
        
    def tryConnect(self):
        self.socket = socket.socket()
        self.socket.settimeout(2)
        self.socket.connect(self.address)
        self.socket.settimeout(0.1)
        self.socket = ssl.wrap_socket(
            self.socket,
            ssl_version=SSL_VERSION,
            server_side=False,
            cert_reqs=ssl.CERT_NONE
        )

    def onDisconnected(self):
        if not self.reconnect:
            self.running = False
            self.connected = False
        else:
            try:
                self.tryConnect()
            except (ConnectionError, ssl.SSLError, socket.timeout):
                pass

    def receive(self, packet: bytes):
        try:
            packet = Packet.fromPacked(packet)
            if packet.getHash() in self.client.hashlist:
                return
            self.client.hashlist[packet.getHash()] = time.time()
            packed = packet.getPacked()
            self.client.broadcast(int.to_bytes(len(packed), 2, "big") + packed)
            self.client.parse(packet)
        except Exception as e:
            pass

    def send(self, packet):
        if self.alive:
            try:
                self.socket.send(packet)
                return True
            except Exception:
                return False
        return False

    def run(self):
        self.running = True
        while self.running:
            try:
                packet_size = self.socket.recv(2)
            except (socket.timeout, ssl.SSLError, OSError):
                continue
            except OSError:
                self.onDisconnected()
                continue

            if packet_size == b"":
                self.onDisconnected()
                continue

            packet_size = int.from_bytes(packet_size, "big")
            packet = self.socket.recv(packet_size)
            if packet == b"":
                self.onDisconnected()
                continue
            self.receive(packet)

    def close(self):
        self.reconnect = False
        if self.running:
            self.running = False
        time.sleep(0.2)
        if self.alive:
            self.socket.close()

    @property
    def alive(self):
        if self.reconnect:
            return True
        return self.connected