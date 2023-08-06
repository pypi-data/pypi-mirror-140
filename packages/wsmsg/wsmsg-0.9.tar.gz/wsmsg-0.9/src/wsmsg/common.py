import logging
from uuid import UUID, uuid4
from typing import NamedTuple
from asyncio import Event
from msgpack import packb, unpackb
from websockets.legacy.protocol import WebSocketCommonProtocol 

logger = logging.getLogger(__package__)

class Message(NamedTuple):
    uid: bytes
    reference: bytes
    channel: str
    subject: str
    data: any
    def __repr__(self):
        elements = [
            UUID(bytes=self.uid).hex,
            UUID(bytes=self.reference).hex if self.reference else None,
            self.channel,
            self.subject
        ]
        return f"<Message({', '.join([str(e) for e in elements])})>"

class Connection(object):

    def __init__(self, ws: WebSocketCommonProtocol, debug=False):
        self._debug = debug
        self._ws = ws
        logging.debug(f"Creating connection {self.id}")
        self._ack = Event()
        self._ack.set()
        # self._unacked: list[bytes] = []

    def __repr__(self):
        return f"<Connection {self.id.hex}>"

    @property
    def id(self) -> UUID:
        return self._ws.id

    async def send(self, msg: Message):
        logging.debug(f"{self.id.hex[20:]} -> {msg}")
        await self._ws.send(packb(msg))
        await self._ack.wait()

    async def recv(self) -> Message:
        while True:
            msg = Message(*unpackb(await self._ws.recv()))
            logging.debug(f"{self.id.hex[20:]} <- {msg}")
            if msg.channel == 'system' and msg.subject == 'ack':
                self._ack.set()
                continue
            else:
                await self._ws.send(packb(Message(uuid4().bytes, msg.uid, 'system', 'ack', None)))
            return msg

    async def close(self):
        logging.debug(f"Closing connection {self.id.hex}")
        # self._unacked = []
        # self._CTS.set()
        self._ack.set()
        if not self._ws.closed:
            await self._ws.close()

