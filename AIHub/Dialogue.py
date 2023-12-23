import asyncio
from typing import Callable
from loguru import logger

from .Endpoint import Endpoint


class Dialogue:
    def __init__(self, endpoint: Endpoint = None, endpoint_config_path: str = None):
        self.messages = []
        if not endpoint_config_path and not endpoint:
            raise ValueError("Either endpoint or endpoint_path must be specified")
        if endpoint_config_path and not endpoint:
            endpoint = Endpoint.load_from_yaml(endpoint_config_path)
        self.endpoint = endpoint
        self.lock = asyncio.Lock()

    def get_messages(self):
        return self.messages

    def clear_messages(self):
        self.messages = []

    async def send_message(self, message: str, **kwargs) -> str:
        async with self.lock:
            self.messages.append({"role": "user", "content": message})
            logger.debug(f"Sending message {message} to endpoint {self.endpoint.name}")
            response = await self.endpoint.send_message(self.messages, **kwargs)
            logger.debug(f"Received response {response} from endpoint {self.endpoint.name}")
            self.messages.append({"role": "assistant", "content": response})
            return response

    def send_message_with_callback(self, message: str, callback: Callable[[str], None], **kwargs) -> None:
        async def async_send_message():
            response = await self.send_message(message, **kwargs)
            callback(response)

        asyncio.create_task(async_send_message())
