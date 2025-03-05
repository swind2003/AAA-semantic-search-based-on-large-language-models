#!/usr/bin/env python3.10.13
"""测试向量数据库存储可用性.

Copyright 2023 Li Jinhua.
License(GPL)
Author: Li Jinhua
"""
from llms.utils import haystack_utils


haystack_utils.save_docs(
    "E:/CodeFile/multilingual_project/chataaa/roles_db"
    "/000000/00000000001")
# haystack_utils.create_document_store(
#     "E:/CodeFile/multilingual_project/chataaa/roles_db"
#     "/000000/00000000001")
haystack_utils.load_document_store(
    "E:/CodeFile/multilingual_project/chataaa/roles_db"
    "/000000/00000000001")

# f = open('E:/CodeFile/multilingual_project/chataaa/roles_db'
#          '/000000/00000000001/doc_dir/case_1.txt')
# line = f.readline().strip()
# print(line)
