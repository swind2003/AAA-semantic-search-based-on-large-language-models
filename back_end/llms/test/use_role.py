#!/usr/bin/env python3.10.13
"""仅用于测试功能，对外提供的 role api.

Copyright 2023 Li Jinhua.
License(GPL)
Author: Li Jinhua
"""
import requests

url = 'https://23w5971n67.goho.co/'  # 服务器的实际IP地址


def post_question(user_id, llm, role_id, prompt, openai_api_key, query):
    """
    从服务器向llm主机发出请求
    :param user_id:
    :param role_id:
    :param prompt:
    :param openai_api_key:
    :param query:
    :return:
    """
    question_data = {
        "user_id": user_id,
        "role_id": role_id,
        "llm": llm,
        "prompt": prompt,
        # 后续应该添加history
        "openai_api_key": openai_api_key,
        "query": query
    }
    answer = requests.post(url, json=question_data)

    if answer.status_code == 200:
        return answer.json()
    else:
        print("请求失败，状态码错误如下:", answer.status_code)
        return None


if __name__ == '__main__':
    user_id = "000000"
    role_id = "00000000001"
    llm = "gpt-3.5-turbo"
    prompt = ""
    # 后续应该添加history
    openai_api_key = "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"
    query = "因冲突将他人打伤，导致右额部粉碎性骨折、右眼眶骨骨折，请问应该如何判处？"
    model_answer = post_question(
        user_id, role_id, llm, prompt, openai_api_key, query)
    model_response = model_answer.get('response')
    print(model_response)
