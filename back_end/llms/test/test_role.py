#!/usr/bin/env python3.10.13
"""测试role模块运行情况.

Copyright 2023 Li Jinhua.
License(GPL)
Author: Li Jinhua
"""
from llms import role


test_role = role.Role("000000", "1", "gpt-3.5-turbo", "")
test_role.determine_db_path()
# print(role.db_path)
answer = test_role.use_role(
    "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",
    "因冲突将他人打伤，导致右额部粉碎性骨折、右眼眶骨骨折，请问应该如何判处？"
)
print(answer)
