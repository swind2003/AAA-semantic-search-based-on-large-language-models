#!/usr/bin/env python3.10.13
"""llm Role.
该文件必须放在路径chataaa-llms下, 否则获取路径会产生问题

Copyright 2023 Li Jinhua.
License(GPL)
Author: Li Jinhua
"""
import os
from utils import haystack_utils


class Role(object):
    """
    用户创建在系统中的大模型角色
    """
    user_id = ""
    role_id = ""
    llm = ""
    prompt = ""
    db_path = ""  # 必须是该形式: "../<user_id>/<role_id>"

    def __init__(self, user_id, role_id, llm, prompt):
        """
        加载一个角色
        :param user_id: 用户的唯一标识id
        :param role_id: 角色的唯一标识id
        :param llm: 选用的大模型
        :param prompt: 角色的提示词
        """
        self.user_id = user_id
        self.role_id = role_id
        self.llm = llm
        if prompt is None:
            self.prompt = ""
        else:
            self.prompt = prompt

    def determine_db_path(self):
        """
        在llm主机中使用, 确定存储路径
        :return:
        """
        # 获取项目根目录
        root_path = os.path.abspath(os.path.pardir)
        root_path = root_path.replace('\\', '/')
        roles_db_path = "%s/roles_db" % root_path
        self.db_path = "%s/%s/%s" % (roles_db_path, self.user_id, self.role_id)

    def create_role(self):
        """
        将当前的角色创建进入GPU主机 (存储资料库的主机)
        :return:
        """
        if self.db_path == "":
            print("请先使用determine_db_path()来确定存储路径")
        doc_dir_path = self.db_path + "/doc_dir"
        faiss_index_path = self.db_path + "/faiss_index"
        print("doc_dir_path", doc_dir_path)
        print("faiss_index_path", faiss_index_path)
        if not os.path.exists(doc_dir_path):
            os.makedirs(doc_dir_path)
        if not os.path.exists(faiss_index_path):
            os.makedirs(faiss_index_path)

    def use_role(self, openai_api_key, question):
        """
        使用角色进行对话
        :param openai_api_key: openai密钥
        :param question: 传入问题
        :return: 获得回复
        """
        self.determine_db_path()
        document_store = haystack_utils.load_document_store(self.db_path)
        generative_pipeline = haystack_utils.create_generative_qa_pipeline(
            document_store, openai_api_key, self.prompt)
        answer = haystack_utils.use_qa_pipeline(generative_pipeline, question)
        return answer

    def clean_doc_dir(self):
        """
        清除文档存储
        Returns:

        """
        doc_dir = self.db_path + "/doc_dir"
        file_list = os.listdir(doc_dir)
        for file in file_list:
            file_path = os.path.join(doc_dir, file)
            if os.path.isfile(file_path):
                os.remove(file_path)

    def create_store(self):
        """
        根据文档内容生成向量数据库, 生成后删除文档本体
        :return:
        """
        if self.db_path == "":
            print("请先使用determine_db_path()来确定存储路径")
        haystack_utils.create_document_store(self.db_path)
        self.clean_doc_dir()

    def add_files_to_store(self):
        """
        将文档内容添加到向量数据库, 生成后删除文档本体
        :return:
        """
        if self.db_path == "":
            print("请先使用determine_db_path()来确定存储路径")
        haystack_utils.add_files_to_store(self.db_path)
        self.clean_doc_dir()
