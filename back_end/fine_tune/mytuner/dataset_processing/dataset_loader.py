#!/usr/bin/env python3.11.2
"""处理数据集加载任务.

Copyright 2023 Zheyun Liu.
License(GPL)
Author: Zheyun Liu.
"""
import os
from typing import TYPE_CHECKING, Optional
from datasets import load_dataset
if TYPE_CHECKING:
    from datasets import Dataset
    from mytuner.hyper_parameter import DataArguments


EXT2TYPE = {
    "csv": "csv",
    "json": "json",
    "jsonl": "json",
    "txt": "text"
}


def get_dataset(data_args):
    """获取数据集.

    Args:
        data_args(DataArguments): 数据参数.

    Returns:
        Optional[Dataset]形式的数据集.
    """
    # 数据集最大样本量
    max_samples = data_args.max_samples
    # 要返回的数据集
    dataset: Optional["Dataset"] = None
    # 数据集参数
    dataset_attr = data_args.my_dataset
    if not dataset_attr:
        return dataset
    # 数据集路径
    dataset_path = os.path.join(
        data_args.dataset_dir, dataset_attr.dataset_name)
    if os.path.isfile(dataset_path):
        # 数据文件类型
        data_path = EXT2TYPE.get(dataset_attr.dataset_name.split(".")[-1], None)
    else:
        raise ValueError("File not found.")
    # 加载数据集
    dataset = load_dataset(
        data_path,
        data_files=dataset_path,
        split=data_args.split,
        streaming=data_args.streaming,
    )
    # 限制数据集最大样本量
    if max_samples is not None:
        max_samples_temp = min(len(dataset), max_samples)
        dataset = dataset.select(range(max_samples_temp))
    # 将数数据集中的列重命名
    for column_name in ["prompt", "query", "response", "history"]:
        # 这个函数在需要动态地访问对象属性时非常有用，特别是当属性名称是在运行时确定的情况下
        column_value = getattr(dataset_attr, column_name)
        if column_value and column_value != column_name:
            dataset = dataset.rename_column(column_value, column_name)
    # 添加系统提示词
    if dataset_attr.system_prompt:
        system_prompt = dataset_attr.system_prompt
        if data_args.streaming:
            dataset = dataset.map(lambda _: {"system": system_prompt})
        else:
            dataset = dataset.add_column(
                "system", [system_prompt] * len(dataset))
    return dataset
