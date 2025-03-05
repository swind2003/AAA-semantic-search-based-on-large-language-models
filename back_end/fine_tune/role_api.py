#!/usr/bin/env python3.10.13
"""对外提供的 role api.

Copyright 2023 Li Jinhua.
License(GPL)
Author: Li Jinhua
"""
import fastapi
from transformers import AutoTokenizer, AutoModel
import uvicorn
import json
import datetime
import torch

import mytuner


app = fastapi.FastAPI()


@app.post("/query")
async def create_item(request: fastapi.Request):
    """
    获取服务器发来的使用请求并返回结果
    :param request:
    :return:
    """
    global MY_MODEL
    # 获取时间等信息
    now = datetime.datetime.now()
    time = now.strftime("%Y-%m-%d %H:%M:%S")
    # try:
    # 获取json格式数据包内容
    json_post_raw = await request.json()
    json_post = json.dumps(json_post_raw)
    json_post_list = json.loads(json_post)
    prompt = json_post_list.get('prompt')
    question = json_post_list.get('question')
    prompt = prompt + question
    history = json_post_list.get('history')
    max_length = json_post_list.get('max_length')
    top_p = json_post_list.get('top_p')
    temperature = json_post_list.get('temperature')

    user_id = json_post_list.get('user_id')
    role_id = json_post_list.get('role_id')
    openai_api_key = json_post_list.get('openai_api_key')
    # 调用模型的部分-----------------------------
    response = MY_MODEL.chat(prompt)[0][0]
    # ----------------------------------------
    # 生成回复
    answer = {
        "code": "200",
        "response": response,
        "time": time
    }
    log = "[" + time + "] " + '", prompt:"' + prompt + \
          '", response:"' + repr(response) + '"'
    print(log)
    # except:
    #     # 生成回复
    #     answer = {
    #         "status": "400",
    #         "response": "调用llm出现问题",
    #         "time": time
    #     }
    return answer


if __name__ == '__main__':
    MY_MODEL = mytuner.ChatModel(mytuner.chat_args)
    uvicorn.run(app, host='0.0.0.0', port=8080, workers=1)
