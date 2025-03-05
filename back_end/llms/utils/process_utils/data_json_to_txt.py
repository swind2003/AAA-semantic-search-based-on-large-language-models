#!/usr/bin/env python3.10.13
"""将标准json格式数据集转化为txt格式.

Copyright 2023 Li Jinhua.
License(GPL)
Author: Li Jinhua
"""
import os
import json

# 指定文件夹路径
folder_path = "data_train/"
# 如果文件夹不存在，创建它
if not os.path.exists(folder_path):
    os.makedirs(folder_path)

# 打开 json 文件, 将内容转化为一系列 txt 文件
with open('data_train.json', encoding="utf-8") as f:
    data = json.load(f)
    # 逐个处理 JSON 数据并将其写入 txt 文件
    for i, item in enumerate(data):
        # 生成文件名，如 "case_1.txt", "case_2.txt"
        file_name = f"case_{i + 1}.txt"
        file_path = folder_path + file_name
        # 基本案情
        fact = item.get("fact")
        # 相关刑法条例
        relevant_articles = item.get("meta").get("relevant_articles")
        # 罪名
        accusation = item.get("meta").get("accusation")
        # 罚金
        punish_of_money = item.get("meta").get("punish_of_money")
        # 被告人
        criminals = item.get("meta").get("criminals")
        # 是否死刑
        death_penalty = item.get("meta").get("term_of_imprisonment").\
            get("death_penalty")
        # 监禁
        imprisonment = item.get("meta").get("term_of_imprisonment").\
            get("imprisonment")
        # 是否无期
        life_imprisonment = item.get("meta").get("term_of_imprisonment").\
            get("life_imprisonment")

        with open(file_path, "w", encoding="utf-8") as file:
            file.write("基本案情：")
            file.write(fact)
            file.write("\n")
            file.write("\n")
            file.write("相关刑法条例：")
            relevant_articles_as_strings = [
                str(relevant_article) for relevant_article in relevant_articles]
            file.write(", ".join(relevant_articles_as_strings))
            file.write("\n")
            file.write("罪名：")
            file.write(", ".join(accusation))
            file.write("\n")
            file.write("罚金（元）：")
            file.write(str(punish_of_money))
            file.write("\n")
            file.write("被告人：")
            file.write(", ".join(criminals))
            file.write("\n")
            file.write("是否死刑：")
            if death_penalty:
                file.write("是")
                file.write("\n")
            else:
                file.write("否")
                file.write("\n")
            file.write("监禁（月）：")
            file.write(str(imprisonment))
            file.write("\n")
            file.write("是否无期：")
            if life_imprisonment:
                file.write("是")
                file.write("\n")
            else:
                file.write("否")
                file.write("\n")
