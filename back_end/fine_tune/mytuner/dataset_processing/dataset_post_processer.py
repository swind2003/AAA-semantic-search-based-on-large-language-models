#!/usr/bin/env python3.11.2
"""处理数据集后处理任务.

Copyright 2023 Zheyun Liu.
License(GPL)
Author: Zheyun Liu.
"""
from typing import TYPE_CHECKING, Dict
if TYPE_CHECKING:
    from datasets import Dataset
    from transformers import TrainingArguments
    from mytuner.hyper_parameter import DataArguments


def split_dataset(
    dataset: "Dataset",
    data_args: "DataArguments",
    training_args: "TrainingArguments"
) -> Dict[str, "Dataset"]:
    """将数据集拆分为训练集和评估集或验证集（可选）.

        Args:
            dataset (Dataset): 待拆分的数据集.
            data_args ("DataArguments"): 数据相关参数.
            training_args ("TrainingArguments"): 训练相关参数.

        Returns:
            Dict[str, "Dataset"]: 包含拆分后数据集的字典，包括训练集和（可选的）评估集.
        """
    if training_args.do_train:
        if data_args.val_size > 1e-6:
            if data_args.streaming:
                val_set = dataset.take(int(data_args.val_size))
                train_set = dataset.skip(int(data_args.val_size))
                dataset = dataset.shuffle(
                    buffer_size=data_args.buffer_size, seed=training_args.seed)
                return {"train_dataset": train_set, "eval_dataset": val_set}
            else:
                val_size = int(data_args.val_size) \
                    if data_args.val_size > 1 \
                    else data_args.val_size
                dataset = dataset.train_test_split(
                    test_size=val_size, seed=training_args.seed)
                return {
                    "train_dataset": dataset["train"],
                    "eval_dataset": dataset["test"]
                }
        else:
            if data_args.streaming:
                dataset = dataset.shuffle(
                    buffer_size=data_args.buffer_size, seed=training_args.seed)
            return {"train_dataset": dataset}
    else:
        return {"eval_dataset": dataset}
