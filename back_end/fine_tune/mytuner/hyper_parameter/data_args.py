#!/usr/bin/env python3.11.2
"""用于存储和管理用于模型训练和评估的数据相关参数的类.

Copyright 2023 Zheyun Liu.
License(GPL)
Author: Zheyun Liu.
"""
import os
import json
from typing import Literal, Optional
from dataclasses import dataclass, field


@dataclass
class DatasetAttr:
    """包含了数据集属性的定义.

    Attributes:
        dataset_name(Optional[str]): 数据集名称.
        system_prompt(Optional[str]): 系统提示词.
        ranking(Optional[bool]): 用于标识数据集是否包含排名相关的信息.
        formatting(Optional[Literal["alpaca", "sharegpt"]]): 格式化类型.
        prompt(Optional[str]): 提示词的键名.
        query(Optional[str]): 查询的键名.
        response(Optional[str]): 输出的键名.
        history(Optional[str]): 历史询问的记录.
    """
    dataset_name: Optional[str] = None
    system_prompt: Optional[str] = None
    ranking: Optional[bool] = False
    formatting: Optional[Literal["alpaca", "sharegpt"]] = "alpaca"
    prompt: Optional[str] = "instruction"
    query: Optional[str] = "input"
    response: Optional[str] = "output"
    history: Optional[str] = None

    def __repr__(self) -> str:
        return self.dataset_name


@dataclass
class DataArguments:
    """类是用于定义模型训练和评估过程中所需参数配置的数据结构.

    它包含了许多参数字段，用于指定模型训练和评估的各种设置.

    Attributes:
        seed(Optional[int]): 用于init_for_training函数的参数.
        my_dataset(Optional[DatasetAttr]): 用于init_for_training函数的参数.
        dataset(Optional[str]): 提供的要使用的数据集的名称.
        dataset_dir(Optional[str]): 包含数据集的文件夹的名称.
        split(Optional[str]): 用于训练和评估的数据集划分.
        cutoff_len(Optional[int]): 分词后模型输入的最大长度.
        train_on_prompt(Optional[bool]): 是否在提示符中禁用掩码.
        streaming(Optional[bool]): 启用数据集流.
        buffer_size(Optional[int]): 用于在数据流中随机采样的缓冲区的大小.
        interleave_probs(Optional[float]): 从数据集中抽样数据的概率.
        overwrite_cache(Optional[bool]): 覆盖缓存的训练集和评估集.
        preprocessing_num_workers(Optional[int]): 用于预处理的进程数.
        max_samples(Optional[int]): 出于调试目的, 截断数据集的样例数量.
        eval_num_beams(Optional[int]): 用于评估的梁数.
            这个参数将被传递给`model.generate`.
        ignore_pad_token_for_loss(Optional[bool]): 在损失计算中是否忽略填充标签对应的标记.
        system_prompt(Optional[str]): 系统提示在用户查询前添加.
        val_size(Optional[float]): 开发集的大小, 应该是一个整数或一个范围为`[0,1)`的浮点数.
        sft_packing(Optional[bool]): 在监督微调阶段对问题和答案进行打包.
        cache_path(Optional[str]): 保存或加载预处理数据集的路径.
    """
    dataset: Optional[str] = field(
        default=None,
        metadata={"help": "The name of provided dataset(s) to use."}
    )
    dataset_dir: Optional[str] = field(
        default="data",
        metadata={"help": "The name of the folder containing datasets."}
    )
    split: Optional[str] = field(
        default="train",
        metadata={"help": "Which dataset split to use for "
                          "training and evaluation."}
    )
    cutoff_len: Optional[int] = field(
        default=1024,
        metadata={
            "help":
                "The maximum length of the model inputs after tokenization."}
    )
    train_on_prompt: Optional[bool] = field(
        default=False,
        metadata={"help": "Whether to disable the mask on the prompt or not."}
    )
    streaming: Optional[bool] = field(
        default=False,
        metadata={"help": "Enable dataset streaming."}
    )
    buffer_size: Optional[int] = field(
        default=16384,
        metadata={
            "help": "Size of the buffer to randomly sample examples "
                    "from in dataset streaming."}
    )
    interleave_probs: Optional[float] = field(
        default=None,
        metadata={
            "help": "Probabilities to sample data from datasets."}
    )
    overwrite_cache: Optional[bool] = field(
        default=False,
        metadata={"help": "Overwrite the cached training and evaluation sets."}
    )
    preprocessing_num_workers: Optional[int] = field(
        default=None,
        metadata={
            "help": "The number of processes to use for the preprocessing."}
    )
    max_samples: Optional[int] = field(
        default=None,
        metadata={
            "help": "For debugging purposes, "
                    "truncate the number of examples for each dataset."}
    )
    eval_num_beams: Optional[int] = field(
        default=None,
        metadata={
            "help": "Number of beams to use for evaluation. "
                    "This argument will be passed to `model.generate`"}
    )
    ignore_pad_token_for_loss: Optional[bool] = field(
        default=True,
        metadata={
            "help": "Whether to ignore the tokens corresponding to "
                    "padded labels in the loss computation or not."}
    )
    system_prompt: Optional[str] = field(
        default=None,
        metadata={
            "help": "System prompt to add before the user query."}
    )
    val_size: Optional[float] = field(
        default=0,
        metadata={
            "help": "Size of the development set, "
                    "should be an integer or a float in range `[0,1)`."}
    )
    sft_packing: Optional[bool] = field(
        default=False,
        metadata={
            "help": "Packing the questions and answers "
                    "in the supervised fine-tuning stage."}
    )
    cache_path: Optional[str] = field(
        default=None,
        metadata={"help": "Path to save or load the preprocessed datasets."}
    )

    def __post_init__(self):
        """在对象初始化后执行参数的合法性检查和验证."""
        if self.streaming and 1e-6 < self.val_size < 1:
            raise ValueError("Streaming mode should have an integer val size.")

        if self.streaming and self.max_samples is not None:
            raise ValueError("`max_samples` is incompatible with `streaming`.")

        if self.streaming and self.cache_path:
            raise ValueError("`cache_path` is incompatible with `streaming`.")

    def init_for_training(self, input_seed):
        """用于在模型训练阶段初始化数据参数.

        Args:
            input_seed(int): 设置随机数生成器的种子，以确保在模型训练的不同阶段
            （例如数据集加载、数据处理、参数初始化）中使用相同的种子值，生成的随机序列是可预测的.
        """
        # 随机数种子
        self.seed = input_seed
        # 获取数据集名称
        name = self.dataset.strip()
        # 获取数据集配置信息
        try:
            with open(os.path.join(self.dataset_dir, "dataset_info.json"),
                      "r") as f:
                dataset_info = json.load(f)
        except Exception:
            if self.dataset is not None:
                raise ValueError(
                    "Cannot find dataset_info.json in `dataset_dir`.")
            dataset_info = None
        if name not in dataset_info:
            raise ValueError(
                "Undefined dataset {} in dataset_info.json".format(name)
            )
        dataset_attr = DatasetAttr(
            dataset_name=dataset_info[name]["file_name"],
        )
        if "columns" in dataset_info[name]:
            dataset_attr.prompt = dataset_info[name]["columns"].get(
                "prompt", None)
            dataset_attr.query = dataset_info[name]["columns"].get("query",
                                                                   None)
            dataset_attr.response = dataset_info[name]["columns"].get(
                "response", None)
            dataset_attr.history = dataset_info[name]["columns"].get(
                "history", None)
        dataset_attr.ranking = dataset_info[name].get("ranking", False)
        dataset_attr.system_prompt = self.system_prompt
        # 处理好的数据集
        self.my_dataset = dataset_attr
