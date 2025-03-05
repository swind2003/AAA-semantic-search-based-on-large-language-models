#!/usr/bin/env python3.10.13
"""对外提供的 role api.

Copyright 2023 Li Jinhua.
License(GPL)
Author: Li Jinhua
"""
import datetime
import json
import os
import shutil
import typing
import fastapi
import uvicorn
import role

app = fastapi.FastAPI()


@app.post("/query")
async def create_item(request: fastapi.Request):
    """
    获取服务器发来的使用请求并返回结果
    :param request:
    :return:
    """
    # 获取时间等信息
    now = datetime.datetime.now()
    time = now.strftime("%Y-%m-%d %H:%M:%S")
    try:
        # 获取json格式数据包内容
        json_post_raw = await request.json()
        json_post = json.dumps(json_post_raw)
        json_post_list = json.loads(json_post)
        user_id = json_post_list.get('user_id')
        role_id = json_post_list.get('role_id')
        print("user_id", user_id)
        print("role_id", role_id)
        llm = json_post_list.get('llm')
        prompt = json_post_list.get('prompt')
        openai_api_key = json_post_list.get('openai_api_key')
        question = json_post_list.get('question')
        # 创建角色
        api_role = role.Role(user_id, role_id, llm, prompt)
        # 使用角色进行对话
        response = api_role.use_role(openai_api_key, question)
        # 生成回复
        answer = {
            "code": "200",
            "response": response,
            "time": time
        }
        log = "[" + time + "] " + '", prompt:"' + prompt + \
              '", response:"' + repr(response) + '"'
        print(log)
    except Exception as error:
        print("调用llm出现问题\n", error)
        # 生成回复
        answer = {
            "status": "400",
            "response": "调用llm出现问题",
            "time": time
        }
    return answer


@app.post("/create_role")
async def create_role(
        files: typing.List[fastapi.UploadFile] = fastapi.File(...),
        user_id: str = fastapi.Form(None),
        role_id: str = fastapi.Form(None),
        llm: str = fastapi.Form(None),
        prompt: str = fastapi.Form(None)
):
    """
    获取服务器发来的文档并创建角色
    :param files:
    :param user_id:
    :param role_id:
    :param llm:
    :param prompt:
    :return:
    """
    try:
        print("User ID:", user_id)
        print("Role ID:", role_id)
        print("LLM:", llm)
        print("Prompt:", prompt)
        # 创建角色
        api_role = role.Role(user_id, role_id, llm, prompt)
        api_role.determine_db_path()
        api_role.create_role()
        doc_dir_path = api_role.db_path + "/doc_dir/"
        # 接收文件
        for file in files:
            res = await file.read()
            with open(doc_dir_path + file.filename, "wb") as f:
                f.write(res)
        # 生成向量数据库
        api_role.create_store()
    except Exception as error:
        print("创建角色失败\n", error)
        return {
            "code": "400"
        }
    return {
        "code": "200"
    }


@app.post("/add_files")
async def add_files(
        files: typing.List[fastapi.UploadFile] = fastapi.File(...),
        user_id: str = fastapi.Form(None),
        role_id: str = fastapi.Form(None),
        llm: str = fastapi.Form(None),
        prompt: str = fastapi.Form(None)
):
    """
    获取服务器发来的文档并添加到数据库中
    :param files:
    :param user_id:
    :param role_id:
    :param llm:
    :param prompt:
    :return:
    """
    try:
        print("User ID:", user_id)
        print("Role ID:", role_id)
        print("LLM:", llm)
        print("Prompt:", prompt)
        # 创建角色
        api_role = role.Role(user_id, role_id, llm, prompt)
        api_role.determine_db_path()
        doc_dir_path = api_role.db_path + "/doc_dir/"
        # 接收文件
        for file in files:
            res = await file.read()
            with open(doc_dir_path + file.filename, "wb") as f:
                f.write(res)
        # 生成向量数据库
        api_role.add_files_to_store()
    except Exception as error:
        print("添加文档失败\n", error)
        return {
            "code": "400"
        }
    return {
        "code": "200"
    }


@app.post("/delete_role")
async def delete_role(request: fastapi.Request):
    """
    获取服务器发来的请求, 删除角色
    Args:
        request:

    Returns:

    """
    try:
        # 获取json格式数据包内容
        json_post_raw = await request.json()
        json_post = json.dumps(json_post_raw)
        json_post_list = json.loads(json_post)
        user_id = json_post_list.get('user_id')
        role_id = json_post_list.get('role_id')
        print("删除角色")
        print("User ID:", user_id)
        print("Role ID:", role_id)
        # 创建角色
        api_role = role.Role(user_id, role_id, "", "")
        api_role.determine_db_path()
        dir_path = api_role.db_path
        # 删除一个文件夹，无论里面是否有文件或文件夹
        shutil.rmtree(dir_path)
    except Exception as e:
        print("删除角色失败\n", e)
        return {
            "code": "200"
        }
    return {
        "code": "200"
    }


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8080, workers=1)
