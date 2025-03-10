#!/usr/bin/env python3.10.13
"""仅用于测试.

Copyright 2023 Li Jinhua.
License(GPL)
Author: Li Jinhua
"""
import os
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
from langchain.llms import ChatGLM
from langchain.prompts import PromptTemplate
from langchain.tools import BaseTool, Tool, tool
from langchain.vectorstores import Chroma
from llms.test import tools
from llms.utils import langchain_utils

from langchain.agents import Tool, AgentExecutor, LLMSingleActionAgent, \
    AgentOutputParser
from langchain.prompts import StringPromptTemplate
from langchain.llms import OpenAI
from langchain.chains import LLMChain
from typing import List, Union
from langchain.schema import AgentAction, AgentFinish, OutputParserException
import re

if __name__ == "__main__":
    # # 接入chatGPT
    llm = ChatOpenAI(
        temperature=0,
        openai_api_key="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")
    # 接入chatGLM
    # endpoint_url = "http://127.0.0.1:8080"
    # llm = ChatGLM(
    #     endpoint_url=endpoint_url,
    #     max_token=80000,
    #     top_p=0.9
    # )
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
            name="criminal_law_case_inquiry",
            func=qa.run,
            description="useful when you need to answer questions about criminal law"
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

    # Set up a prompt template
    class CustomPromptTemplate(StringPromptTemplate):
        # The template to use
        template: str
        # The list of tools available
        tools: List[Tool]

        def format(self, **kwargs) -> str:
            # Get the intermediate steps (AgentAction, Observation tuples)
            # Format them in a particular way
            intermediate_steps = kwargs.pop("intermediate_steps")
            thoughts = ""
            for action, observation in intermediate_steps:
                thoughts += action.log
                thoughts += f"\nObservation: {observation}\nThought: "
            # Set the agent_scratchpad variable to that value
            kwargs["agent_scratchpad"] = thoughts
            # Create a tools variable from the list of tools provided
            kwargs["tools"] = "\n".join(
                [f"{tool.name}: {tool.description}" for tool in self.tools])
            # Create a list of tool names for the tools provided
            kwargs["tool_names"] = ", ".join([tool.name for tool in self.tools])
            return self.template.format(**kwargs)

    prompt = CustomPromptTemplate(
        template=template,
        tools=tools,
        # This omits the `agent_scratchpad`, `tools`, and `tool_names` variables because those are generated dynamically
        # This includes the `intermediate_steps` variable because that is needed
        input_variables=["input", "intermediate_steps"]
    )

    # 输出解析器
    class CustomOutputParser(AgentOutputParser):
        def parse(self, llm_output: str) -> Union[AgentAction, AgentFinish]:
            # Check if agent should finish
            if "Final Answer:" in llm_output:
                return AgentFinish(
                    # Return values is generally always a dictionary with a single `output` key
                    # It is not recommended to try anything else at the moment :)
                    return_values={"output": llm_output.split("Final Answer:")[
                        -1].strip()},
                    log=llm_output,
                )
            # Parse out the action and action input
            regex = r"Action\s*\d*\s*:(.*?)\nAction\s*\d*\s*Input\s*\d*\s*:[\s]*(.*)"
            match = re.search(regex, llm_output, re.DOTALL)
            if not match:
                raise OutputParserException(
                    f"Could not parse LLM output: `{llm_output}`")
            action = match.group(1).strip()
            action_input = match.group(2)
            # Return the action and action input
            return AgentAction(tool=action,
                               tool_input=action_input.strip(" ").strip('"'),
                               log=llm_output)

    output_parser = CustomOutputParser()
    # LLM chain consisting of the LLM and a prompt
    llm_chain = LLMChain(llm=llm, prompt=prompt)

    tool_names = [tool.name for tool in tools]
    agent = LLMSingleActionAgent(
        llm_chain=llm_chain,
        output_parser=output_parser,
        stop=["\nObservation:"],
        allowed_tools=tool_names
    )

    agent_executor = AgentExecutor.from_agent_and_tools(agent=agent,
                                                        tools=tools,
                                                        verbose=True)

    print("代理构建完成, 现在运行代理")
    agent_executor.run("因冲突将人打至左额部粉碎性骨折、左眼眶骨骨折，请问应该怎么判处？")

    # agent = initialize_agent(
    #     tools,
    #     llm,
    #     agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    #     stop=["\nObservation:"],
    #     verbose=True
    # )
    # print("代理构建完成, 现在运行代理")
    # agent.run(
    #     "因冲突将人打至左额部粉碎性骨折、左眼眶骨骨折，请问应该怎么判处？"
    # )
