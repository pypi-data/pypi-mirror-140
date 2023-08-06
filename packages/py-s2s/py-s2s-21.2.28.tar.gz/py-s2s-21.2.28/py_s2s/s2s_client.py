import asyncio
import random
import string
import uuid
from dataclasses import dataclass, field
import json as _json
import typing

import aio_pika
from aio_pika import Queue

from py_s2s.s2s_connection_config import RabbitConfig


@dataclass
class GenericResponse:
    body: bytes = b'{}'
    status_code: int = 200
    headers: typing.Dict[str, str] = field(default_factory=dict)


class RMQClient:
    def __init__(self, service_name, exchange_name, queue_name_prefix):
        self.queue_name_prefix = queue_name_prefix
        self.service_name = service_name
        self.exchange_name = exchange_name
        self.connection = None
        self.channel = None
        self.queue_name = None
        self.queue: Queue = None
        self.exchange = None
        self._response_futures = {}

    async def bind(self, topic):
        if not self.queue:
            raise Exception('We don\'t have a queue open yet.')
        await self.queue.bind(self.exchange_name, routing_key=topic)

    async def connect(self, config=RabbitConfig):
        if self.connection:
            return
        for _ in range(10):
            # try to connect 10 times
            try:
                self.connection = await aio_pika.connect_robust(
                    f'amqp://{config.username}:{config.password}@{config.host}:{config.port}/',
                    client_properties={'client_properties': {'service': self.service_name}}
                )
                break
            except ConnectionError:
                # try again
                await asyncio.sleep(3)
        else:
            raise ConnectionError(f'Could not connect to rabbit at {config.host} '
                                  f'with username {config.username}')

        self.channel = await self.connection.channel(on_return_raises=True)
        self.exchange = await self.channel.declare_exchange(self.exchange_name, aio_pika.ExchangeType.TOPIC)

        if not self.queue_name:
            letters = string.ascii_lowercase + string.digits
            rand_str = ''.join(random.choice(letters) for _ in range(8))
            self.queue_name = f'{self.queue_name_prefix}-q-{rand_str}'

        self.queue: aio_pika.Queue = await self.channel.declare_queue(self.queue_name,
                                                                      durable=False,
                                                                      arguments={'x-expires': 200000})
        asyncio.create_task(self.response_handler(self.channel))

    async def close(self):
        if self.connection:
            await self.connection.close()

    async def send_request(self, path,  body=None, headers=None) -> GenericResponse:
        if type(body) is dict:
            body = _json.dumps(body)
        ex = self.exchange
        message_id = str(uuid.uuid4())
        if 'x-correlation-id' in headers:
            correlation_id = headers.get('x-correlation-id')
            del headers['x-correlation-id']
        else:
            correlation_id = str(uuid.uuid4())

        try:
            await ex.publish(
                aio_pika.Message(
                    body.encode(),
                    delivery_mode=aio_pika.DeliveryMode.NOT_PERSISTENT,
                    message_id=message_id,
                    correlation_id=correlation_id,
                    reply_to=self.queue_name,
                    headers=headers,
                    expiration=27,
                ),
                routing_key=path,
                mandatory=True)
        except aio_pika.exceptions.DeliveryError as e:
            return GenericResponse(b'{"error": {"message": "Not Found"}}', 404)
        except Exception as e:
            print(e)
        response = asyncio.Future()
        self._response_futures[message_id] = response
        try:
            return await asyncio.wait_for(response, timeout=27)
        except asyncio.TimeoutError:
            self._response_futures.pop(message_id, None)
            raise

    async def response_handler(self, channel: aio_pika.Channel):
        while True:
            try:
                def format_header_val(v):
                    if isinstance(v, list):
                        return [format_header_val(i) for i in v]
                    if isinstance(v, bytes):
                        return v.decode()
                    if isinstance(v, str):
                        return v
                    if isinstance(v, int):
                        return str(v)
                    if isinstance(v, bool):
                        return str(v).lower()
                    raise ValueError(f'Unhandled header type {type(v)}')

                async with self.queue.iterator(no_ack=True) as q:
                    async for message in q:
                        async with message.process(ignore_processed=True):
                            status = message.headers.get('status-code', 500)
                            headers = {k: format_header_val(v) for k, v in message.headers.items()}

                            if 'status-code' in headers:
                                headers.pop('status-code')
                            if message.content_type:
                                headers['content-type'] = message.content_type
                            if message.content_encoding:
                                headers['content-encoding'] = message.content_encoding

                            r = GenericResponse(body=message.body,
                                                status_code=int(status),
                                                headers=headers)

                            f: asyncio.Future = self._response_futures.pop(
                                message.message_id, None)
                            if f and not f.done():
                                f.set_result(r)
            except Exception as e:
                import traceback
                traceback.print_exc()
                print(e, type(e))
