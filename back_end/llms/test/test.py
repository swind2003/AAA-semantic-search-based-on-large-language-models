#!/usr/bin/env python3.10.13
"""仅用于测试langchain.

Copyright 2023 Li Jinhua.
License(GPL)
Author: Li Jinhua
"""
import os
from langchain.agents import AgentType, initialize_agent
from langchain.chains import RetrievalQA
from langchain.llms import ChatGLM
from langchain.prompts import PromptTemplate
from langchain.vectorstores import Chroma
from llms.utils import langchain_utils

from langchain.agents import Tool, AgentExecutor, LLMSingleActionAgent, \
    AgentOutputParser

if __name__ == "__main__":
    # # 接入chatGPT
    # llm = ChatOpenAI(
    # temperature=0,
    # openai_api_key="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")
    # 接入chatGLM
    endpoint_url = "http://127.0.0.1:8080"
    llm = ChatGLM(
        endpoint_url=endpoint_url,
        max_token=80000,
        top_p=0.9
    )
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

    prompt_template = """Use the following pieces of context to answer the question at the end. If you don't know the answer, just say that you don't know, don't try to make up an answer.

    {context}

    Question: {question}
    Answer:"""
    PROMPT = PromptTemplate(
        template=prompt_template, input_variables=["context", "question"]
    )
    chain_type_kwargs = {"prompt": PROMPT}
    # history = []
    # chain_type_kwargs = {"prompt": PROMPT, "history": history}

    qa = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type='stuff',
        retriever=retriever,
        chain_type_kwargs=chain_type_kwargs
        # return_source_documents=True
    )
    print("嗨嗨嗨")
    # response = qa.run(
    #     "因冲突将人打至左额部粉碎性骨折、左眼眶骨骨折，请问应该怎么判处？")
    # print(response)
    # response = qa.run(
    #     "你记得我叫什么名字吗？")
    # print(response)

    # tools = [tools.CustomSearchTool()]
    tools = [
        Tool(
            name="chinese_criminal_law_case_inquiry",
            func=qa.run,
            description="useful when you need to answer questions "
                        "about Chinese criminal law"
        )]
    print("工具构建完成")

    # 构建代理
    template = """Answer the following questions as best you can. You have access to the following tools:

    {tools}

    Use the following format:

    Question: the input question you must answer
    Thought: you should always think about what to do
    Action: the action to take, should be one of [{tool_names}]
    Action Input: the input to the action
    Observation: the result of the action
    ... (this Thought/Action/Action Input/Observation can repeat 1 times)
    Thought: I now know the final answer
    Final Answer: the final answer to the original input question

    Begin!

    Question: {input}
    {agent_scratchpad}"""

    agent = initialize_agent(
        tools,
        llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        stop=["\nObservation:"],
        verbose=True
    )
    print("代理构建完成, 现在运行代理")
    agent.run(
        "因冲突将人打至左额部粉碎性骨折、左眼眶骨骨折，请问应该怎么判处？"
    )
