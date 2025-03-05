#!/usr/bin/env python3.10.13
"""仅用于测试.

Copyright 2023 Li Jinhua.
License(GPL)
Author: Li Jinhua
"""
import os
from langchain.vectorstores import Chroma
from langchain.tools import BaseTool, Tool, tool
from typing import Optional, Type
from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from llms.utils import langchain_utils


def search_db(query: str) -> str:
    """
    useful for when you need to answer questions about law.
    """
    # 创建数据库检索, 并从中寻找答案 (后续创建数据库检索的部分可以另写一个函数)
    # 加载模型
    embeddings = langchain_utils.load_embedding_model("text2vec3")
    # 加载数据库
    if not os.path.exists('../vectorstore'):
        # 如果数据不存在, 就根据books创建
        documents = langchain_utils.load_documents("books")
        vector_db = langchain_utils.store_chroma(documents, embeddings)
    else:
        # 如果存在数据, 就直接使用之前的数据
        vector_db = Chroma(
            persist_directory='VectorStore', embedding_function=embeddings)

    retriever = vector_db.as_retriever(search_kwargs={"k": 1})
    # 使用 VectorStoreRetriever 进行检索
    retrieved_docs = retriever.get_relevant_documents(query)

    # 在这里可以根据检索结果生成您的响应
    response = "No relevant documents found."
    if retrieved_docs:
        # 可以根据检索到的文档来生成响应
        response = "Found relevant documents:\n"
        for doc in retrieved_docs:
            response += f"Title: {doc.metadata['source']}\n"
            response += f"Text: {doc.page_content}\n\n"
    return response


class CustomSearchTool(BaseTool):
    """
    测试能否使用自定义agent的Tool
    """
    name = "chinese_criminal_law_case_inquiry"
    description = "useful when you need to answer questions about Chinese criminal law"
    # name = "中国刑法案例查询"
    # description = "当你需要回答有关中国刑法的问题时很有用"

    def _run(
            self, query: str,
            run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Use the tool."""
        return search_db(query)

    async def _arun(
            self, query: str,
            run_manager: Optional[AsyncCallbackManagerForToolRun] = None
    ) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("custom_search does not support async")


# my_response = search_db("因冲突将人打至左额部粉碎性骨折、左眼眶骨骨折，请问应该怎么判处？")
# print(my_response)
