import asyncio
from AIHub import Endpoint


async def endpoint_example():
    baidu_endpoint = Endpoint.load_from_yaml('../LocalConfig/Endpoints/baidu.yaml')
    response = await baidu_endpoint.send_message([{"role": "user", "content": "你好！你是谁？"}], only_text=True)
    print("Received response:", response)
    print("Status: ", baidu_endpoint.get_status())

    openai_endpoint = Endpoint.load_from_yaml('../LocalConfig/Endpoints/openai_official.yaml')
    response = await openai_endpoint.send_message([{"role": "user", "content": "你好！你是谁？"}], only_text=False)
    print("Received response:", response)
    print("Status: ", baidu_endpoint.get_status())

    openai_endpoint = Endpoint.load_from_yaml('../LocalConfig/Endpoints/openai_mirror_1.yaml')
    response = await openai_endpoint.send_message([{"role": "user", "content": "你好！你是谁？"}], only_text=False)
    print("Received response:", response)
    print("Status: ", baidu_endpoint.get_status())


if __name__ == '__main__':
    asyncio.run(endpoint_example())
