#!/usr/bin/env python3.10.13
"""仅用于测试功能，对外提供的 api 使用.

Copyright 2023 Li Jinhua.
License(GPL)
Author: Li Jinhua
"""
import requests
import json

url = 'https://23w5971n67.goho.co/'  # 服务器的实际IP地址


def post_question(prompt, history):
    question_data = {
        "prompt": prompt,
        "history": history,
        "max_length": 2048,
        "top_p": 0.7,
        "temperature": 0.95
    }
    answer = requests.post(url, json=question_data)

    if answer.status_code == 200:
        return answer.json()
    else:
        print("Request failed with status code:", answer.status_code)
        return None


if __name__ == '__main__':
    user_prompt = "你好"
    user_history = []
    model_answer = post_question(user_prompt, user_history)
    model_response = model_answer.get('response')
    user_history = model_answer.get('history')
    print(model_response)
    user_prompt = "请复述我说的话"
    model_answer = post_question(user_prompt, user_history)
    model_response = model_answer.get('response')
    user_history = model_answer.get('history')
    print(model_response)
