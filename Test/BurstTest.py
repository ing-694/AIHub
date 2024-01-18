import asyncio

from AIHub import Endpoint


async def main():
    endpoint = Endpoint.load_from_yaml('../LocalConfig/Endpoints/baidu.yaml')

    messages = [[{
        "role": "user",
        "content": "你好！"
    }], [{
        "role": "user",
        "content": "你是谁？"
    }], [{
        "role": "user",
        "content": "你是机器人吗？"
    }], [{
        "role": "user",
        "content": "你叫什么名字？"
    }], [{
        "role": "user",
        "content": "你是男是女？"
    }], [{
        "role": "user",
        "content": "你几岁了？"
    }], [{
        "role": "user",
        "content": "你是哪里人？"
    }], [{
        "role": "user",
        "content": "你会做什么？"
    }], [{
        "role": "user",
        "content": "你有男朋友吗？"
    }], [{
        "role": "user",
        "content": "你有女朋友吗？"
    }]]

    futures = [asyncio.create_task(endpoint.send_message(msg)) for msg in messages]

    # 等待所有消息处理完成
    responses = await asyncio.gather(*futures)

    # 打印响应
    for response in responses:
        print(response)

    # 关闭 Endpoint 实例
    await endpoint.close()


# 运行主函数
asyncio.run(main())
