#!/usr/bin/env python3.10.13
"""使用langchain为项目提供工具.

Copyright 2023 Li Jinhua.
License(GPL)
Author: Li Jinhua
"""
from langchain.document_loaders import DirectoryLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings.huggingface import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma

# 加载embedding
embedding_model_dict = {
    "ernie-tiny": "nghuyong/ernie-3.0-nano-zh",
    "ernie-base": "nghuyong/ernie-3.0-base-zh",
    "text2vec": "GanymedeNil/text2vec-large-chinese",
    "text2vec2": "uer/sbert-base-chinese-nli",
    "text2vec3": "shibing624/text2vec-base-chinese",
}


def load_documents(directory="books"):
    """
    加载文档, 并对文档进行分割
    :param directory:
    :return: split_docs
    """
    loader = DirectoryLoader(directory)
    my_documents = loader.load()
    # for document in documents:
    #     print(document)
    text_spliter = CharacterTextSplitter(chunk_size=256, chunk_overlap=0)
    split_docs = text_spliter.split_documents(my_documents)
    return split_docs


def load_embedding_model(model_name="text2vec3"):
    """
    加载embedding模型
    :param model_name:
    :return:
    """
    encode_kwargs = {"normalize_embeddings": False}
    model_kwargs = {"device": "cuda:0"}
    return HuggingFaceEmbeddings(
        model_name=embedding_model_dict[model_name],
        model_kwargs=model_kwargs,
        encode_kwargs=encode_kwargs
    )


def store_chroma(docs, my_embeddings, persist_directory="vectorstore"):
    """
    产生embedding向量
    :param docs:
    :param my_embeddings:
    :param persist_directory:
    :return:
    """
    db = Chroma.from_documents(
        docs, my_embeddings, persist_directory=persist_directory)
    db.persist()
    return db
