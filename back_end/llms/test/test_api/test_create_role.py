#!/usr/bin/env python3.10.13
"""仅用于测试创建角色功能的运行情况.

Copyright 2023 Li Jinhua.
License(GPL)
Author: Li Jinhua
"""
import os
import requests


if __name__ == "__main__":
    server_url = "https://23w5971n67.goho.co/create_role"
    folder_path = "E:\\CodeFile\\back_end\\PythonFile\\test\\files"

    files_to_send = []
    additional_info = {
        "user_id": "123",
        "role_id": "12",
        "llm": "gpt-3.5-turbo",
        "prompt": ""
    }

    # 遍历文件夹下的所有文件
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path):  # 确保是文件而不是文件夹
            files_to_send.append(("files", open(file_path, "rb")))
    # 发送请求，包含多个文件
    response = requests.post(server_url, files=files_to_send, data=additional_info)
    print(response)
