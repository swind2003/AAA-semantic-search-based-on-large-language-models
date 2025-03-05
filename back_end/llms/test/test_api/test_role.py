#!/usr/bin/env python3.10.13
"""仅用于测试role模块运行情况.

Copyright 2023 Li Jinhua.
License(GPL)
Author: Li Jinhua
"""
import requests


endpoint_url = "https://23w5971n67.goho.co/query"

question_data = {
    "user_id": "000000",
    "role_id": "1",
    "llm": "gpt-3.5-turbo",
    "prompt": "",
    # 后续应该添加history
    "openai_api_key": "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",
    "question": "因冲突将他人打伤，导致右额部粉碎性骨折、右眼眶骨骨折，请问应该如何判处？"
}
# question_data = {
#     "user_id": "123",
#     "role_id": "12",
#     "llm": "gpt-3.5-turbo",
#     "prompt": "",
#     # 后续应该添加history
#     "openai_api_key": "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",
#     "question": "你好"
# }
answer = requests.post(endpoint_url, json=question_data)
print(answer)
