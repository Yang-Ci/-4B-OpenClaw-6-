import os
from http import HTTPStatus
from dashscope import Generation

# 设置 API Key
# 方法 1：直接设置
api_key = "sk-8b65dfd067f44a629e8b8965fb2d285a"

# 方法 2：从环境变量读取（推荐）
# api_key = os.getenv("DASHSCOPE_API_KEY")

# 使用 Qwen 模型
response = Generation.call(
    model='qwen-turbo',  # 模型名称
    prompt='给我讲一个故事',
    api_key=api_key)

if response.status_code != HTTPStatus.OK:
    print(f'request_id={response.request_id}')
    print(f'code={response.status_code}')
    print(f'message={response.message}')
    print(f'请参考文档：https://help.aliyun.com/zh/model-studio/developer-reference/error-code')
else:
    print(response.output.text)