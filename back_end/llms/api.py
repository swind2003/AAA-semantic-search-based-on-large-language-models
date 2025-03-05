#!/usr/bin/env python3.10.13
"""对前端页面提供的语义搜索功能api.

Copyright 2023 Li Jinhua.
License(GPL)
Author: Li Jinhua
"""
import datetime
import json
import torch
import uvicorn
from fastapi import FastAPI, Request
from transformers import AutoTokenizer, AutoModel

DEVICE = "cuda"
DEVICE_ID = "0"
CUDA_DEVICE = f"{DEVICE}:{DEVICE_ID}" if DEVICE_ID else DEVICE


def torch_gc():
    """
    清理 PyTorch GPU 内存.
    Returns:

    """
    if torch.cuda.is_available():
        with torch.cuda.device(CUDA_DEVICE):
            torch.cuda.empty_cache()
            torch.cuda.ipc_collect()


app = FastAPI()


@app.post("/")
async def create_item(request: Request):
    """
    处理 POST 请求，执行语义搜索并返回结果.
    Args:
        request:

    Returns:

    """
    global MODEL, TOKENIZER
    json_post_raw = await request.json()
    json_post = json.dumps(json_post_raw)
    json_post_list = json.loads(json_post)
    prompt = json_post_list.get('prompt')
    history = json_post_list.get('history')
    max_length = json_post_list.get('max_length')
    top_p = json_post_list.get('top_p')
    temperature = json_post_list.get('temperature')
    response, history = MODEL.chat(TOKENIZER,
                                   prompt,
                                   history=history,
                                   max_length=max_length if max_length else 2048,
                                   top_p=top_p if top_p else 0.7,
                                   temperature=temperature if temperature else 0.95)
    # print("\n\n\n这里是history:\n", history, "\n\n\n")
    now = datetime.datetime.now()
    time = now.strftime("%Y-%m-%d %H:%M:%S")
    answer = {
        "response": response,
        "history": history,
        "status": 200,
        "time": time
    }
    log = "[" + time + "] " + '", prompt:"' + prompt + '", response:"' + repr(response) + '"'
    print(log)
    torch_gc()
    return answer


if __name__ == '__main__':
    LLM_PATH = r"E:\files\huggingface\hub\models--THUDM--chatglm2-6b"
    TOKENIZER = AutoTokenizer.from_pretrained(LLM_PATH, trust_remote_code=True)
    MODEL = AutoModel.from_pretrained(LLM_PATH, trust_remote_code=True).cuda()
    # 多显卡支持，使用下面三行代替上面两行，将num_gpus改为你实际的显卡数量
    # model_path = "THUDM/chatglm2-6b"
    # TOKENIZER = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
    # MODEL = load_model_on_gpus(model_path, num_gpus=2)
    MODEL.eval()
    uvicorn.run(app, host='0.0.0.0', port=8080, workers=1)
