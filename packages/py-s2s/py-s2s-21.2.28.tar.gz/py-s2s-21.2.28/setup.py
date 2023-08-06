# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['py_s2s']

package_data = \
{'': ['*']}

install_requires = \
['aio-pika>=7.1,<8.0']

setup_kwargs = {
    'name': 'py-s2s',
    'version': '21.2.28',
    'description': 'Python service to service communication over rabbitmq ephemeral queues',
    'long_description': '# Py S2S\n\nThis is a simple publish and subscribe for a response over RabbitMQ. This is only half of two parts needed for "http over rabbit" intended for service to service communication.\n\n# notice\nThis is an asyncio library that uses aio-pika.\n\n# example\n\n```py\nasync def run():\n    conn = RabbitConfig(\n        host=\'localhost\',\n        port=5672,\n        username=\'guest\',\n        password=\'guest\',\n        exchange=\'/\',\n        queue_name=\'my_queue\'  # This is a prefix, it will append a random string to the end of this.\n    )\n    c = Service2Service(service_name=\'Test Service\', config=conn)\n    headers = {\n        \'authorization\': \'Bearer XX\',\n        \'content-type\': \'application/json\'\n    }\n    r = await c.request(\'accounts.load\', dict(test=True, name=\'bob\'), headers=headers)\n    print(r)  # Returns a `S2S GenericResponse` dataclass\n\n```',
    'author': 'Skyler Lewis',
    'author_email': 'skyler@hivewire.co',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://hivewire.co',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
