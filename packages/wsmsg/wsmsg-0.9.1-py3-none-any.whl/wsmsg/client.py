import threading, logging
from uuid import UUID, uuid4
from fnmatch import fnmatch
from typing import Union, Awaitable, Callable, NamedTuple
from asyncio import get_event_loop, create_task, wait, wait_for, run_coroutine_threadsafe, run, gather
from asyncio import Future, Queue, Event
from asyncio import FIRST_COMPLETED
from inspect import isfunction, iscoroutinefunction
from websockets.exceptions import ConnectionClosed, ConnectionClosedOK
from websockets.client import connect

from .common import Message, Connection

logger = logging.getLogger(__package__)

class ClientSub(NamedTuple):
    channel: str
    subject: str

class Client(object):
    
    def __init__(self, endpoint: str, host: str = 'localhost', port: str = 1234, key: str = None, reconnect=True):
        self.loop = get_event_loop()
        self.host = host
        self.port = port
        self.endpoint = endpoint
        self.key = key
        self.uri = f"ws://{self.host}:{self.port}/{self.endpoint}"
        self._subs: set[ClientSub] = set()
        self._outbound = Queue()
        self._callbacks: dict[str, dict[str, Union[Awaitable, Callable]]] = dict()
        self._replies: dict[bytes, Future] = dict()
        self._conn: Connection = None
        self._connected = None
        self._reconnect = reconnect
        self.connected = Event()
        self.disconnected = Event()
        logger.debug(f"Created {self} ({endpoint}, {host}, {port}, {key})")

    async def _executor_callback(self, callback: Callable, msg: Message):
        await self.loop.run_in_executor(None, callback, ClientThreadsafe(self), msg)

    async def _main(self):
        async for ws in connect(self.uri, open_timeout=1):
            logger.info(f"Connected to {self.uri}")
            self._conn = Connection(ws)
            self._connected.set()
            async def rx():
                global rxed
                logger.debug("Starting RX task...")
                while True:
                    try:
                        msg = await self._conn.recv()
                        if msg.reference and msg.reference in self._replies:
                            logger.debug(f"Setting future {self._replies[msg.reference]} result {msg}")
                            self._replies.pop(msg.reference).set_result(msg)
                            continue
                        if msg.channel in self._callbacks:
                            for filter, callback in self._callbacks[msg.channel].items():
                                if fnmatch(msg.subject, filter):
                                    if iscoroutinefunction(callback):
                                        logger.debug(f"Scheduling coroutine {callback} for {msg}")
                                        create_task(callback(self, msg))
                                    elif isfunction(callback):
                                        logger.debug(f"Scheduling executor {callback} for {msg}")
                                        create_task(self._executor_callback(callback, msg))
                    except:
                        break
            async def tx():
                logger.debug("Starting TX task...")
                global sent
                while True:
                    try:
                        msg: Message = await self._outbound.get()
                        await self._conn.send(msg)
                        self._outbound.task_done()
                    except:
                        break
            pending = []
            # re-register any subscription callbacks
            for channel, filters in self._callbacks.items():
                for filter in filters:
                    await self.publish(
                        Message(uuid4().bytes, None, 'system', 'subscribe.channel', (self.endpoint, channel, filter))
                    )
            # re-register any pending replies
            for uid in self._replies:
                await self.publish(
                    Message(uuid4().bytes, None, 'system', 'subscribe.message', (uid))
                )
            try:
                done, pending = await wait({
                    create_task(rx()),
                    create_task(tx())
                }, return_when=FIRST_COMPLETED)
                for task in done:
                    exc = task.exception()
                    if exc and not isinstance(exc, ConnectionClosedOK) \
                        and not isinstance(exc, KeyboardInterrupt):
                        logger.error(f"* Exception: {exc}")
            finally: 
                for task in pending:
                    task.cancel()
                await gather(*pending, return_exceptions=True)
            if self._conn:
                await self._conn.close()
            self.connected.clear()
            if not self._reconnect:
                break
            else:
                logger.info(f"Connection lost... reconnecting")
        logger.info(f"Disconnected!")
        self.disconnected.set()

    @property
    def pending(self):
        return self._outbound.qsize()

    async def connect(self):
        self._connected = Event()
        self._task = create_task(self._main())
        await self._connected.wait()

    async def close(self):
        self._reconnect = False
        if self._conn:
            await self._conn.close()

    async def publish(self, msg: Message):
        await self._outbound.put(msg)

    async def subscribe(self, channel: str, subject: str, callback: Union[Awaitable, Callable]):
        if channel not in self._callbacks:
            self._callbacks[channel] = dict()
        self._callbacks[channel][subject] = callback
        await self.publish(
            Message(uuid4().bytes, None, 'system', 'subscribe.channel', (self.endpoint, channel, '*'))
        )

    async def unsubcribe(self, channel:str):
        if channel in self._callbacks:
            await self.publish(
                Message(uuid4().bytes, None, 'system', 'unsubscribe.channel', (self.endpoint, channel))
            )
            self._callbacks.pop(channel)

    async def request(self, msg: Message, timeout=None) -> Message:
        reply = get_event_loop().create_future()
        self._replies[msg.uid] = reply
        await self.publish(
            Message(uuid4().bytes, None, 'system', 'subscribe.message', (self.endpoint, msg.uid))
        )
        await self.publish(msg)
        if timeout:
            return await wait_for(reply, timeout)
        else:
            return await reply

class ClientThread(threading.Thread):

    def __init__(self, endpoint: str, host: str = 'localhost', port: int = 1234, key: str = None):
        super().__init__(None, None, 'MessageClient')
        self.name = 'MessageClient'
        self.daemon = True
        self.host = host
        self.port = port
        self.endpoint = endpoint
        self.key = key
        self._stop = None
        self._client = None
        self.connected = threading.Event()

    async def main(self):
        self._stop = Event()
        self._client = Client(self.endpoint, self.host, self.port, self.key)
        await self._client.connect()
        self.connected.set()
        await self._stop.wait()
        self.connected.clear()
        await self._client.close()

    def run(self):
        run(self.main())
    
    def start(self):
        super().start()
        if not self.connected.wait(timeout=5):
            self.stop()
            raise Exception("Connection timeout")

    def stop(self):
        self._stop.set()

    def publish(self, msg: Message):
        run_coroutine_threadsafe(self._client.publish(msg), self._client.loop).result()

    def subscribe(self, channel: str, subject: str, callback: Callable):
        run_coroutine_threadsafe(self._client.subscribe(channel, subject, callback), self._client.loop).result()

    def unsubscribe(self, channel: str):
        run_coroutine_threadsafe(self._client.unsubscribe(channel), self._client.loop).result()

    def request(self, msg: Message, timeout=None) -> Message:
        return run_coroutine_threadsafe(self._client.request(msg, timeout), self._client.loop).result()


class ClientThreadsafe(object):

    def __init__(self, client: Client):
        self._client = client

    def publish(self, msg: Message):
        run_coroutine_threadsafe(self._client.publish(msg), self._client.loop).result()

    def subscribe(self, channel: str, subject: str, callback: Callable):
        run_coroutine_threadsafe(self._client.subscribe(channel, subject, callback), self._client.loop).result()

    def unsubscribe(self, channel: str):
        run_coroutine_threadsafe(self._client.unsubscribe(channel), self._client.loop).result()

    def request(self, msg: Message, timeout=None) -> Message:
        return run_coroutine_threadsafe(self._client.request(msg, timeout), self._client.loop).result()

    