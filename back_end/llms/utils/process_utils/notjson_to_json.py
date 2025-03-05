#!/usr/bin/env python3.10.13
"""将非标准的数据集格式转化为标准json格式.

Copyright 2023 Li Jinhua.
License(GPL)
Author: Li Jinhua
"""


# 打开原始文本文件和目标文本文件
with open("data_train.txt", "r", encoding="utf-8") as original_file,\
        open("data_train.json", "w", encoding="utf-8") as output_file:
    # 添加开头的 [
    output_file.write("[" + "\n")
    lines = original_file.readlines()
    # 逐行读取原始文件
    for line in lines[:-1]:
        # 移除行尾的换行符
        line = line.strip()
        # 如果行不为空，则在行尾添加逗号
        if line:
            line += ","
        # 将处理后的行写入目标文件
        output_file.write(line + "\n")
    # 处理最后一行（不添加逗号）
    last_line = lines[-1] + "\n"
    output_file.write(last_line)
    # 添加结尾的 ]
    output_file.write("]" + "\n")
