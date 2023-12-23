import asyncio
from AIHub import Dialogue


async def dialogue_example_1():
    # 直接读取本地Endpoint配置文件，创建Dialogue实例
    dialogue = Dialogue(endpoint_config_path='./LocalConfig/Endpoints/baidu_endpoint.yaml')

    # 异步发送消息并获取纯文本回复
    response = await dialogue.send_message("你好！你是谁？")
    print("Received response:", response)

    # 再次发送消息，并使用回调函数处理回复
    # Dialogue会自动维护消息历史，因此AI服务可以根据上下文进行回复
    def my_callback(res):
        print("Received response with callback:", res)

    dialogue.send_message_with_callback("刚刚我说了啥？", my_callback)

    await asyncio.sleep(10)


async def dialogue_example_2():
    # 直接读取本地Endpoint配置文件，创建Dialogue实例
    dialogue = Dialogue(endpoint_config_path='./LocalConfig/Endpoints/openai_official.yaml')

    # 异步发送消息并获取纯文本回复
    response = await dialogue.send_message("你好！你是谁？", system_prompt="请你使用json格式、使用英文进行回答", json_format=True)
    print("Received response:", response)

    # 再次发送消息，并使用回调函数处理回复
    # Dialogue会自动维护消息历史，因此AI服务可以根据上下文进行回复
    def my_callback(res):
        print("Received response with callback:", res)

    dialogue.send_message_with_callback("刚刚我说了啥？", my_callback)

    await asyncio.sleep(10)


if __name__ == '__main__':
    # asyncio.run(dialogue_example_1())
    asyncio.run(dialogue_example_2())
