# Py S2S

This is a simple publish and subscribe for a response over RabbitMQ. This is only half of two parts needed for "http over rabbit" intended for service to service communication.

# notice
This is an asyncio library that uses aio-pika.

# example

```py
async def run():
    conn = RabbitConfig(
        host='localhost',
        port=5672,
        username='guest',
        password='guest',
        exchange='/',
        queue_name='my_queue'  # This is a prefix, it will append a random string to the end of this.
    )
    c = Service2Service(service_name='Test Service', config=conn)
    headers = {
        'authorization': 'Bearer XX',
        'content-type': 'application/json'
    }
    r = await c.request('accounts.load', dict(test=True, name='bob'), headers=headers)
    print(r)  # Returns a `S2S GenericResponse` dataclass

```