import time
import threading
import traceback
import requests

from .packet import Packet
from .handler import Handler
from .info import HOSTLIST_ADDRESS

class InvalidPacketSize(Exception):
    pass

class Client:
    def __init__(self, friendly_hosts: list = [], limit_queue = -1):
        self.hosts = list(friendly_hosts)
        self.limit_queue = limit_queue
        self.handler = Handler
        self.handlers = []
        self.offhandlers = []
        self.queue = []
        self.hashlist = {}
        self.running = True
        threading.Thread(target=self._checkforever).start()        
        for host in friendly_hosts:
            try:
                handler = self.handler.connect(host, self, reconnect=True)
                handler.start()
                self.handlers.append(handler)
            except Exception as e: 
                pass

    def parse(self, packet: Packet):
        self.queue.append(packet)
    
    def __next__(self):
        while len(self.queue) == 0:
            continue
        data = self.queue[0]
        del self.queue[0]
        return data.content, data.getHash()

    def next(self):
        return next(self)

    def accept(self):
        return next(self)

    def broadcast(self, packet: bytes):
        count = 0
        for i in self.handlers:
            count += int(i.send(packet))
        return count

    def send(self, data: bytes):
        packet = Packet.new(data)
        packed = packet.getPacked()
        if len(packed) > 2**16:
            raise InvalidPacketSize("Packet size is larger then 65536")
        self.hashlist[packet.getHash()] = time.time()
        return (self.broadcast(int.to_bytes(len(packed), 2, "big") + packed), packet.getHash())

    def _checkforever(self):
        last_check = 0
        while self.running:
            for i in self.handlers:
                if not i.alive:
                    self.handlers.remove(i)
            for h, t in reversed(self.hashlist.items()):
                if time.time() - t > 60*60*24:
                    del self.hashlist[h]
                else:
                    break
            while len(self.queue) > self.limit_queue and self.limit_queue >= 0:
                del self.queue[0]
            if (not HOSTLIST_ADDRESS is None) and (time.time() - last_check > 5):
                last_check = time.time()
                try:
                    conn = requests.get(HOSTLIST_ADDRESS)
                    data = conn.json()
                    for i in data:
                        if i in self.offhandlers:
                            continue
                        try:
                            handler = self.handler.connect(tuple(i), self, reconnect=True)
                            handler.start()
                            self.handlers.append(handler)
                            self.offhandlers.append(i)
                        except Exception as e: 
                            pass
                except:
                    traceback.print_exc()
            time.sleep(0.1)

    def close(self):
        self.running = False
        time.sleep(0.2)
        for i in self.handlers:
            i.close()
