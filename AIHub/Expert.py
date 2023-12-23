import yaml
from typing import Dict
from loguru import logger

from .Endpoint import Endpoint
from .Dialogue import Dialogue


class Expert:
    def __init__(self,
                 endpoint: Endpoint = None,
                 endpoint_config_path: str = None,
                 prompts: Dict[str, str] = None,
                 prompts_config_path: str = None):
        """
        初始化Expert
        :param endpoint: 该Expert使用的Endpoint
        :param endpoint_config_path: 该Expert使用的Endpoint的配置文件路径。endpoint和endpoint_config_path必须指定一个
        :param prompts: 该Expert使用的Prompt字典
        :param prompts_config_path: 该Expert使用的Prompt字典的配置文件路径
        """
        if not endpoint_config_path and not endpoint:
            raise ValueError("Either endpoint or endpoint_path must be specified")
        if endpoint_config_path and not endpoint:
            endpoint = Endpoint.load_from_yaml(endpoint_config_path)
        self.endpoint = endpoint

        self.dialogue = Dialogue(endpoint)

        if prompts_config_path and not prompts:
            with open(prompts_config_path, 'r', encoding='utf-8') as file:
                prompts = yaml.safe_load(file)
        self.prompts = prompts

    @staticmethod
    def _replace_placeholders(template: str, values: Dict[str, str]) -> str:
        # 将模板字符串中的占位符替换为values字典中的值
        result = template
        if not values:
            return result
        for key, value in values.items():
            result = result.replace(f'{{{key}}}', value)
        return result

    async def get_answer(self, message: str = None, prompt_type: str = None,
                         prompt_params: Dict[str, str] = None, **kwargs) -> str:
        """
        使用指定的提示词和参数，获取回答
        当prompt_type不为空时，使用prompt_type对应的提示词作为LLM输入，并使用prompt_params对Prompt进行补全。此时忽略message参数
        当prompt_type为空时，直接使用message作为LLM输入
        不包含上下文
        """
        if prompt_type:
            if prompt_type not in self.prompts:
                raise ValueError(f"Prompt with name '{prompt_type}' not found")

            prompt_template = self.prompts[prompt_type]
            prompt_message = self._replace_placeholders(prompt_template, prompt_params)

            logger.debug(f"Sending prompt '{prompt_type}' with message: {prompt_message}")
            response = await self.endpoint.send_message([{"role": "user", "content": prompt_message}], **kwargs)
            logger.debug(f"Received response: {response}")
        else:
            logger.debug(f"Sending message: {message}")
            response = await self.endpoint.send_message([{"role": "user", "content": message}], **kwargs)
            logger.debug(f"Received response: {response}")

        return response

    async def communicate(self, message: str = None, prompt_type: str = None,
                          prompt_params: Dict[str, str] = None, **kwargs) -> str:
        """
        在一个对话中，使用指定的提示词和参数，获取回答
        当prompt_type不为空时，使用prompt_type对应的提示词作为LLM输入，并使用prompt_params对Prompt进行补全。此时忽略message参数
        当prompt_type为空时，直接使用message作为LLM输入
        自动维护对话上下文。除非调用restart_dialogue，否则对话历史记录将不断累加
        """
        if prompt_type:
            if prompt_type not in self.prompts:
                raise ValueError(f"Prompt with name '{prompt_type}' not found")

            prompt_template = self.prompts[prompt_type]
            prompt_message = self._replace_placeholders(prompt_template, prompt_params)

            logger.debug(f"Sending prompt '{prompt_type}' with message: {prompt_message}")
            response = await self.dialogue.send_message(prompt_message, **kwargs)
            logger.debug(f"Received response: {response}")
        else:
            logger.debug(f"Sending message: {message}")
            response = await self.dialogue.send_message(message, **kwargs)
            logger.debug(f"Received response: {response}")

        return response

    def restart_dialogue(self):
        self.dialogue.clear_messages()
