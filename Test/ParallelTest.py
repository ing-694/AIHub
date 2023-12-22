import asyncio

from AIHub import Endpoint, Dialogue, Expert

baidu_endpoint = Endpoint.load_from_yaml('../LocalConfig/Endpoints/baidu.yaml')
baidu_dialogue = Dialogue(baidu_endpoint)

text = [
    "你好！",
    "你是谁？",
    "你是机器人吗？",
    "你叫什么名字？",
    "你是男是女？",
    "你几岁了？",
    "你是哪里人？",
    "你会做什么？",
    "你有男朋友吗？",
    "你有女朋友吗？",
]


async def do(i: int):
    response = await baidu_dialogue.send_message(text[i])
    print("Received response:", response)


async def main():
    for i in range(10):
        asyncio.create_task(do(i))
    await asyncio.sleep(100)


asyncio.run(main())
