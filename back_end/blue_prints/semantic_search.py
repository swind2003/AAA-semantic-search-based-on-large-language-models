#!/usr/bin/env python3.10.13
"""对前端页面提供的语义搜索功能api.

Copyright 2023 Li Jinhua.
License(GPL)
Author: Li Jinhua
"""
import os
import time
import flask
import flask_login
import requests

import extentions
import module

# /semantic_search
SEMANTIC_SEARCH_BP = flask.Blueprint(
    "semantic_search", __name__, url_prefix="/semantic_search")


@SEMANTIC_SEARCH_BP.route("/query", methods=['GET', 'POST'])
@flask_login.login_required
def query():
    """
    视图函数-从服务器向llm主机发出请求
    code对应的含义:
    200: 成功
    400: 失败
    401: 插入聊天记录失败
    402: 未查到该用户！
    403: 当前查询次数为0！
    404: 没有这个角色类型, llm_type = 0或1
    Returns:

    """
    front_datas = flask.request.get_json()
    llm_type = front_datas.get("llm_type")
    user_id = front_datas.get("user_id")
    chat_window_id = front_datas.get("chat_window_id")
    role_id = front_datas.get("role_id")
    # openai_api_key = front_datas.get("openai_api_key")
    question = front_datas.get("question")
    # print(llm_type)
    user = module.User.query.get(user_id)
    try:
        if not user:
            # 该用户不存在
            return flask.jsonify({
                "code": "402",
                "response": "未查到该用户！",
                "time": "",
                "current_query_times": user.current_query_times
            })
        if user.current_query_times <= 0:
            # 用户当前查询次数为0
            return flask.jsonify({
                "code": "403",
                "response": "当前查询次数为0！",
                "time": "",
                "current_query_times": user.current_query_times
            })
        if llm_type == "0":
            # 使用 内置角色
            role = module.BuiltInRole.query.get(role_id)
            query_role_id_str = "000000"
        elif llm_type == "1":
            # 使用用户自定义角色
            role = module.UserRole.query.get(role_id)
            query_role_id_str = str(user_id)
        else:
            # 没有这个角色类型
            return flask.jsonify({
                "code": "404",
                "response": "没有这个角色类型, llm_type = 0或1",
                "time": "",
                "current_query_times": user.current_query_times
            })
        url = role.module_api + "query"
        llm = role.module_name
        prompt = role.prompt
        # 后续应该添加history
        answer = SemanticSearch.query(
            url, query_role_id_str, str(role_id), llm, prompt, question)
        # 当前可询问次数减一
        user.current_query_times = user.current_query_times - 1
        extentions.DATABASE.session.commit()
        if SemanticSearch.insert_chat_recoder(chat_window_id, question):
            time.sleep(1)
            if SemanticSearch.insert_chat_recoder(
                    chat_window_id, answer.get("response")):
                return flask.jsonify({
                    "code": answer.get("code"),
                    "response": answer.get("response"),
                    "time": answer.get("time"),
                    "current_query_times": user.current_query_times
                })
        print("插入聊天记录失败！")
        return flask.jsonify({
            "code": "401",
            "response": "插入聊天记录失败！",
            "time": "",
            "current_query_times": user.current_query_times
        })
    except Exception as e:
        print("使用模型出现问题\n", e)
        return flask.jsonify({
            "code": "400",
            "response": "使用模型出现问题！",
            "time": "",
            "current_query_times": user.current_query_times
        })


class SemanticSearch(object):
    """
    语义搜索功能
    """

    @staticmethod
    def get_openai_api_key():
        """
        获得api密钥
        Returns:

        """
        # 指定文件夹路径
        folder_path = os.path.abspath("aaa_file") + "\\openai_api_key"
        # folder_path = "E:\\CodeFile\\multilingual_project\\test\\
        # chataaa\\aaa_file\\openai_api_key"
        folder_path = folder_path.replace('\\', '/')
        file_path = f"{folder_path}/openai_api_key.txt"
        # file_path = file_path.replace('/', '\\')
        # print(file_path)
        with open(file_path, 'r', encoding='utf-8') as file:
            openai_api_key = file.read()
        # print(openai_api_key)
        return openai_api_key

    @staticmethod
    def write_openai_api_key(openai_api_key):
        """
        将api密钥写入文档
        Args:
            openai_api_key:

        Returns:

        """
        # 指定文件夹路径
        file_path = "../aaa_file/openai_api_key/openai_api_key.txt"
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(openai_api_key)

    @staticmethod
    def insert_chat_recoder(chat_window_id, content):
        """
        插入聊天记录
        Args:
            chat_window_id:
            content:

        Returns:

        """
        try:
            # 可能出现意外错误
            # 创建chat_recoder
            chat_recoder = module.ChatRecoder(
                chat_window_id=chat_window_id,
                content=content)
            extentions.DATABASE.session.add(chat_recoder)
            extentions.DATABASE.session.commit()
            return True
        except:
            print("出现意外错误")
            return False

    @staticmethod
    def query(
            url, user_id, role_id, llm, prompt, question):
        """
        从服务器向llm主机发出请求
        Args:
            url:
            user_id:
            role_id:
            llm:
            prompt:
            question:

        Returns:

        """
        openai_api_key = SemanticSearch.get_openai_api_key()
        question_data = {
            "user_id": user_id,
            "role_id": role_id,
            "llm": llm,
            "prompt": prompt,
            # 后续应该添加history
            "openai_api_key": openai_api_key,
            "question": question
        }
        answer = requests.post(url, json=question_data)
        return answer.json()

# endpoint_url = "https://23w5971n67.goho.co/"
# answer = SemanticSearch.query(
#     endpoint_url,
#     "000000",
#     "1",
#     "gpt-3.5-turbo",
#     "",
#     "因冲突将他人打伤，导致右额部粉碎性骨折、右眼眶骨骨折，请问应该如何判处？"
# )
# print(answer.get("response"))

# print(SemanticSearch.get_openai_api_key())
