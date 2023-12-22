import datetime
import json
import aiohttp
import yaml
from loguru import logger
from typing import List, Dict, runtime_checkable, Protocol, Any
from openai import AsyncOpenAI


@runtime_checkable
class IMessageSender(Protocol):
    async def send_message(self, message: Any, **kwargs) -> Any:
        pass


class OpenAIMessageSender:
    def __init__(self, api_key: str, model: str, org_id: str = None, api_base: str = None, **kwargs):
        if api_key == "" or api_key is None:
            raise ValueError("API key cannot be empty")
        if not api_key.startswith("sk-"):
            raise ValueError("API key format error")
        if model == "" or model is None:
            raise ValueError("Model cannot be empty")
        if org_id and not org_id.startswith("org-"):
            raise ValueError("Organization ID format error")

        self.org_id = org_id
        self.api_base = api_base
        self.model = model
        self.client = AsyncOpenAI(api_key=api_key, organization=org_id, base_url=api_base)

        non_none_params = {k: v for k, v in self.__dict__.items() if v is not None}
        logger.debug(f"OpenAI Endpoint Created with params: {non_none_params}")

    async def send_message(self, message: List[Dict[str, str]], **kwargs) -> str | Dict[str, str]:
        reportResponse = await self.client.chat.completions.create(
            model=self.model,
            messages=message,
        )
        if kwargs.get("only_text", True):
            return reportResponse.choices[0].message.content
        else:
            return reportResponse.dict()


class BaiduMessageSender:
    def __init__(self, api_key: str, secret_key: str, **kwargs):
        if api_key == "" or api_key is None:
            raise ValueError("API key cannot be empty")
        if secret_key == "" or secret_key is None:
            raise ValueError("Secret key cannot be empty")

        self.api_key = api_key
        self.secret_key = secret_key
        self.access_token = None
        self.token_obtained_time = None

        non_none_params = {k: v for k, v in self.__dict__.items() if v is not None}
        logger.debug(f"Baidu Endpoint Created with params: {non_none_params}")

    @staticmethod
    async def _get_access_token(api_key: str, secret_key: str):
        url = "https://aip.baidubce.com/oauth/2.0/token"
        params = {"grant_type": "client_credentials", "client_id": api_key, "client_secret": secret_key}
        async with aiohttp.ClientSession() as session:
            async with session.post(url, params=params) as response:
                response_json = await response.json()
                return response_json.get("access_token"), datetime.datetime.now()

    async def check_and_refresh_token(self):
        if self.access_token is None or (datetime.datetime.now() - self.token_obtained_time).days >= 25:
            self.access_token, self.token_obtained_time = await self._get_access_token(self.api_key, self.secret_key)
            logger.debug("Refreshing Baidu access token")

    async def send_message(self, message: List[Dict[str, str]], **kwargs) -> str | Dict[str, str]:
        await self.check_and_refresh_token()
        url = f"https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/completions_pro?access_token={self.access_token}"
        payload = json.dumps({"messages": message})
        headers = {'Content-Type': 'application/json'}

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, data=payload) as response:
                response_json = await response.json()
                if kwargs.get("only_text", True):
                    return response_json["result"]
                else:
                    return response_json


class Endpoint:
    def __init__(self, name: str, provider: str, **kwargs):
        self.name = name
        self.provider = provider
        self.kwargs = kwargs

        self.sender = self._create_sender(**self.dict())

    @staticmethod
    def _create_sender(**kwargs) -> IMessageSender:
        try:
            provider = kwargs['provider']
            if provider == 'openai':
                return OpenAIMessageSender(**kwargs)
            elif provider == 'baidu':
                return BaiduMessageSender(**kwargs)
            else:
                raise ValueError(f"Unsupported provider: {provider}")
        except KeyError as e:
            logger.error(f"Error while creating {kwargs['name']}: Missing required argument: {e}")
        except ValueError as e:
            logger.error(f"Error while creating {kwargs['name']}: {e}")
        except Exception as e:
            logger.error(f"Error while creating {kwargs['name']}: Unknown error: {e}")

    async def send_message(self, message: Any, **kwargs) -> Any:
        try:
            return await self.sender.send_message(message, **kwargs)
        except Exception as e:
            logger.error(f"Error while sending message by {self.name}: {str(e)}")

    @classmethod
    def load_from_yaml(cls, file_path: str) -> 'Endpoint':
        with open(file_path, 'r') as file:
            data = yaml.safe_load(file)
            logger.debug(f"Loaded endpoint {data['name']} from {file_path}")
            return cls(**data)

    @classmethod
    def save_to_yaml(cls, endpoint: 'Endpoint', file_path: str) -> None:
        with open(file_path, 'w') as file:
            yaml.dump(endpoint.dict(), file)
            logger.debug(f"Saved endpoint {endpoint.name} to {file_path}")

    @classmethod
    def load_list_from_yaml(cls, file_path: str) -> List['Endpoint']:
        with open(file_path, 'r') as file:
            data = yaml.safe_load(file)
            logger.debug(f"Loaded endpoints from {file_path}")
            return [cls(**endpoint) for endpoint in data]

    @classmethod
    def save_list_to_yaml(cls, endpoints: List['Endpoint'], file_path: str) -> None:
        with open(file_path, 'w') as file:
            yaml.dump([endpoint.dict() for endpoint in endpoints], file)
            logger.debug(f"Saved endpoints to {file_path}")

    def dict(self) -> dict:
        return {
            "name": self.name,
            "provider": self.provider,
            **self.kwargs
        }