import os
from dataclasses import dataclass


@dataclass
class RabbitConfig:
    host: str = os.getenv('S2S_HOST')
    port: int = os.getenv('S2S_PORT')
    username: str = os.getenv('S2S_USERNAME')
    password: str = os.getenv('S2S_PASSWORD')
    exchange: str = os.getenv('S2S_EXCHANGE')
    queue_name: str = os.getenv('S2S_QUEUE_NAME')
