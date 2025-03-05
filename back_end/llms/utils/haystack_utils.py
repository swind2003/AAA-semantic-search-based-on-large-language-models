#!/usr/bin/env python3.10.13
"""使用haystack为项目提供工具.

Copyright 2023 Li Jinhua.
License(GPL)
Author: Li Jinhua
"""
import os
from haystack import document_stores
from haystack import nodes
from haystack import pipelines
from haystack import utils


def save_docs(db_path):
    """该函数暂未完成"""
    doc_dir = "%s/doc_dir" % db_path
    if not os.path.exists(doc_dir):
        os.makedirs(doc_dir)


def docs_preprocess(pending_data):
    """
    数据预处理
    :param pending_data: 待处理数据
    :return: docs 处理好的文件
    """
    # 数据预处理器
    preprocessor = nodes.PreProcessor(
        clean_empty_lines=True,
        clean_whitespace=True,
        clean_header_footer=False,
        split_by="word",
        split_length=100,
        split_overlap=50,
        split_respect_sentence_boundary=True,
    )
    docs = preprocessor.process(pending_data)
    print(f"n_files_input: {len(pending_data)}\nn_docs_output: {len(docs)}")
    return docs


def create_document_store(db_path):
    """
    创建文档FAISS数据库
    :param db_path: 数据存储路径
    :return: document_store FAISS数据库对象
    """
    # 创建文件夹路径
    if not os.path.exists(db_path):
        os.makedirs(db_path)
    # 设定数据库存储位置并创建数据库对象
    sql_url = "sqlite:///%s/faiss_document_store.db" % db_path
    document_store = document_stores.FAISSDocumentStore(sql_url=sql_url)
    # 创建检索器对象
    embedding_model = r"E:\files\huggingface\hub\models--moka-ai--m3e-base"
    retriever = nodes.EmbeddingRetriever(document_store=document_store,
                                         embedding_model=embedding_model,
                                         top_k=3)

    document_store.delete_documents()

    doc_dir = "%s/doc_dir" % db_path
    got_docs = utils.convert_files_to_docs(dir_path=doc_dir,
                                           clean_func=utils.clean_wiki_text,
                                           split_paragraphs=True,
                                           encoding="UTF-8")
    # 数据预处理
    docs = docs_preprocess(got_docs)
    # 数据写入数据库并保存
    document_store.write_documents(docs)
    document_store.update_embeddings(retriever=retriever)
    faiss_index_path = db_path + "/faiss_index"
    if not os.path.exists(faiss_index_path):
        os.makedirs(faiss_index_path)
    document_store.save(faiss_index_path + "/faiss_document_store_index.index")
    return document_store


def load_document_store(db_path):
    """
    加载已经创建好的FAISS数据库
    :param db_path: 数据库路径
    :return: document_store FAISS数据库对象
    """
    # 指定已有的FAISS索引路径
    faiss_index_path = \
        "%s/faiss_index/faiss_document_store_index.index" % db_path
    # 创建FAISSDocumentStore并传递已有的FAISS索引
    document_store = \
        document_stores.FAISSDocumentStore.load(index_path=faiss_index_path)
    # documents = document_store.get_all_documents(return_embedding=True)
    return document_store


def create_generative_qa_pipeline(document_store, openai_api_key, prompt):
    """
    创建生成式QA管道
    :param document_store: FAISS数据库对象
    :param openai_api_key: openai密钥
    :param prompt: 前置提示词
    :return: generative_pipeline 生成式QA管道对象
    """
    # 创建检索器对象
    embedding_model = r"E:\files\huggingface\hub\models--moka-ai--m3e-base"
    retriever = nodes.EmbeddingRetriever(document_store=document_store,
                                         embedding_model=embedding_model,
                                         top_k=3)
    qa_prompt = """
    请根据所给的文件如实回答问题。
    Question:{query}
    Documents:{join(documents)}
    Answer:
    """
    qa_prompt = prompt + qa_prompt
    # prompt模板
    prompt_template = nodes.PromptTemplate(
        prompt=qa_prompt,
        output_parser=nodes.AnswerParser(),
    )
    # 创建节点
    prompt_node = nodes.PromptNode(
        model_name_or_path="gpt-3.5-turbo",
        api_key=openai_api_key,
        default_prompt_template=prompt_template,
        max_length=1000
    )
    # 组建管道
    generative_pipeline = pipelines.Pipeline()
    generative_pipeline.add_node(component=retriever, name="retriever",
                                 inputs=["Query"])
    generative_pipeline.add_node(component=prompt_node, name="prompt_node",
                                 inputs=["retriever"])
    return generative_pipeline


def use_qa_pipeline(generative_pipeline, query):
    """
    使用qa管道
    :param generative_pipeline: 生成式QA管道对象
    :param query: 问题内容
    :return: answer 生成的答案
    """
    response = generative_pipeline.run(query)
    # # 定义正则表达式模式
    # pattern = re.compile(r"'answer': '([^']+)'")
    #
    # # 在回答字符串中搜索匹配项
    # match = pattern.search(str(response))
    #
    # # 提取匹配项的内容
    # if match:
    #     answer = match.group(1)  # 提取答案内容
    #     print(answer)
    # else:
    #     print("未找到匹配项")
    answer = response["answers"][0].answer
    return answer


def add_files_to_store(db_path):
    """
    向原有的向量数据库中添加文件
    Args:
        db_path:

    Returns:

    """
    # 加载已经创建好的FAISS数据库
    document_store = load_document_store(db_path)
    # 创建检索器对象
    embedding_model = r"E:\files\huggingface\hub\models--moka-ai--m3e-base"
    retriever = nodes.EmbeddingRetriever(document_store=document_store,
                                         embedding_model=embedding_model,
                                         top_k=3)
    # 以下操作和创建store时相似
    doc_dir = "%s/doc_dir" % db_path
    got_docs = utils.convert_files_to_docs(dir_path=doc_dir,
                                           clean_func=utils.clean_wiki_text,
                                           split_paragraphs=True,
                                           encoding="UTF-8")
    # 数据预处理
    docs = docs_preprocess(got_docs)
    # 数据写入数据库并保存
    document_store.write_documents(docs)
    document_store.update_embeddings(retriever=retriever)
    faiss_index_path = db_path + "/faiss_index"
    document_store.save(faiss_index_path + "/faiss_document_store_index.index")
    return document_store
