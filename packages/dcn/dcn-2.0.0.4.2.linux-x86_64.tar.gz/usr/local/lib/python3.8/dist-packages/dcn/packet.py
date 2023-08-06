import time
import random
from io import BytesIO
from dataclasses import dataclass

from Crypto.Hash import SHA256

@dataclass
class Packet:
    uuid: bytes
    content: bytes

    @classmethod
    def fromPacked(cls, data: bytes):
        data = BytesIO(data)
        return cls(data.read(16), data.read())

    def getPacked(self) -> bytes:
        return self.uuid + self.content

    def getHash(self) -> bytes:
        return SHA256.new(self.uuid + self.content).digest()

    @staticmethod
    def generateUUID() -> bytes:
        return int.to_bytes(int(time.time() * (2**24)), 11, "big") + int.to_bytes(random.randint(0, 2**40), 5, "big")

    @classmethod
    def new(cls, content: bytes):
        return cls(cls.generateUUID(), content)
