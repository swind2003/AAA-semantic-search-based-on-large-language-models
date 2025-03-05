#!/usr/bin/env python3.11.2
"""处理数据集预处理任务.

Copyright 2023 Zheyun Liu.
License(GPL)
Author: Zheyun Liu.
"""
import os
from typing import TYPE_CHECKING, Any, Dict, List
from datasets import load_from_disk
from mytuner import extras
if TYPE_CHECKING:
    from datasets import Dataset
    from transformers import Seq2SeqTrainingArguments
    from transformers.tokenization_utils import PreTrainedTokenizer
    from mytuner.hyper_parameter import DataArguments


IGNORE_INDEX = -100


def preprocess_dataset(
    dataset,
    tokenizer,
    data_args,
    training_args,
):
    """数据集预处理任务.

    Args:
        dataset(Dataset): 数据集.
        tokenizer(PreTrainedTokenizer): 令牌.
        data_args(DataArguments): 数据相关的参数.
        training_args(Seq2SeqTrainingArguments): 训练参数

    Returns:
        Dataset类型的数据集. 就是经过预处理后的数据集.
    """

    def construct_example(examples: Dict[str, List[Any]]):
        """用于根据输入的示例数据构建对话的各个部分，包括查询、回复、历史记录和系统信息，并返回这些部分的元组.

        使用 range(len(examples["prompt"])) 遍历整个数据集中的样本.
        对于每个样本：
        从输入数据中获取查询和回复部分，分别赋值给 query 和 response 变量.
        如果输入数据中存在包含 "query" 键的部分，且其值在该索引位置存在，则将其与查询部分连接起来作为新的查询 query.
        否则，保持查询部分不变.
        检查输入数据中是否存在历史记录和系统信息，并将它们赋值给 history 和 system，如果不存在则设为 None.

        Args:
            examples(Dict[str, List[Any]]): 一个包含了不同键的列表的字典，包含了模型所需的各种数据.

        Returns:
            返回一个元组，包含了查询、回复、历史记录和系统信息的各个部分:
            Generator[Any, None, None]
        """
        for i in range(len(examples["prompt"])):
            query, response = examples["prompt"][i], examples["response"][i]
            query = query + "\n" + examples["query"][
                i] if "query" in examples and examples["query"][i] else query
            history = examples["history"][i] if "history" in examples else None
            system = examples["system"][i] if "system" in examples else None
            yield query, response, history, system

    def preprocess_supervised_dataset(examples: Dict[str, List[Any]]):
        """用于处理有监督的数据集.

        它构建输入和标签，处理多轮对话数据，根据需求进行编码、截断和生成适用于模型训练的输入序列和标签序列.
        以`<bos> X Y <eos>`格式构建输入，以`<ignore> ... <ignore> Y <eos>`格式构建标签.
        对于多回合的例子，我们只屏蔽每个提示-响应对中的提示部分.

        Args:
            examples(Dict[str, List[Any]]): 一个包含了不同键的列表的字典，包含了模型所需的各种数据.

        Returns:
            其中包含处理后的有监督数据集的输入和标签信息: Dict[str, Any]
        """
        global IGNORE_INDEX
        model_inputs = {"input_ids": [], "attention_mask": [], "labels": []}
        for query, response, history, system in construct_example(examples):
            if not (isinstance(query, str) and isinstance(
                    response, str) and query != "" and response != ""):
                continue
            input_ids, labels = [], []
            for turn_idx, (source_ids, target_ids) in enumerate(
                    template.encode_multiturn(
                            tokenizer, query, response, history, system
                    )):
                total_len = len(source_ids) + len(target_ids)
                max_source_len = int(
                    data_args.cutoff_len * (len(source_ids) / total_len))
                max_target_len = int(
                    data_args.cutoff_len * (len(target_ids) / total_len))
                # 通过模板的 encode_multiturn 方法将输入序列进行编码，
                # 生成 source_ids（即输入部分）和 target_ids（即标签部分）.
                if len(source_ids) > max_source_len:
                    source_ids = source_ids[:max_source_len]
                if len(target_ids) > max_target_len:
                    target_ids = target_ids[:max_target_len]
                # 根据数据长度、配置和模型要求对 source_ids 和 target_ids 进行截断或调整长度.
                if data_args.train_on_prompt:
                    source_mask = source_ids
                elif turn_idx != 0 and template.efficient_eos:
                    source_mask = [tokenizer.eos_token_id] + [IGNORE_INDEX] * (
                                len(source_ids) - 1)
                else:
                    source_mask = [IGNORE_INDEX] * len(source_ids)
                # 将处理好的部分添加到 input_ids 和 labels 中.
                input_ids += source_ids + target_ids
                labels += source_mask + target_ids
            # 针对 efficient_eos 的情况进行特殊处理，根据情况调整 input_ids 和 labels.
            if template.efficient_eos:
                input_ids += [tokenizer.eos_token_id]
                labels += [tokenizer.eos_token_id]
            # 根据 data_args.cutoff_len 处理 input_ids 和 labels 的长度.
            if len(input_ids) > data_args.cutoff_len:
                input_ids = input_ids[:data_args.cutoff_len]
                labels = labels[:data_args.cutoff_len]
            # 将处理好的 input_ids、attention_mask 和 labels 存储到 model_inputs 字典中.
            model_inputs["input_ids"].append(input_ids)
            model_inputs["attention_mask"].append([1] * len(input_ids))
            model_inputs["labels"].append(labels)
        return model_inputs

    def preprocess_packed_supervised_dataset(examples: Dict[str, List[Any]]):
        """处理有监督数据集，特别是针对 "packed" 或者打包的数据.

        该函数用于构建输入和标签对，以适应模型的训练要求.
        以`<bos> X1 Y1 <eos> <bos> X2 Y2 <eos>`格式建立输入.
        以`<ignore> ... <ignore> Y1 <eos> <ignore> ... <ignore> Y2 <eos>`建立标签.

        Args:
            examples(Dict[str, List[Any]]): 一个包含了不同键的列表的字典，包含了模型所需的各种数据.

        Returns:
            其中包含处理后的有监督数据集的输入和标签信息: Dict[str, Any]
        """
        global IGNORE_INDEX
        model_inputs = {"input_ids": [], "attention_mask": [], "labels": []}
        input_ids, labels = [], []
        for query, response, history, system in construct_example(examples):
            if not (isinstance(query, str)
                    and isinstance(response, str)
                    and query != "" and response != ""):
                continue
            for turn_idx, (source_ids, target_ids) in enumerate(
                    template.encode_multiturn(
                        tokenizer, query, response, history, system
                    )):
                if data_args.train_on_prompt:
                    source_mask = source_ids
                elif turn_idx != 0 and template.efficient_eos:
                    source_mask = [tokenizer.eos_token_id] \
                        + [IGNORE_INDEX] * (len(source_ids) - 1)
                else:
                    source_mask = [IGNORE_INDEX] * len(source_ids)
                input_ids += source_ids + target_ids
                labels += source_mask + target_ids
        # 针对 efficient_eos 的情况进行特殊处理，根据情况调整 input_ids 和 labels.
        if template.efficient_eos:
            input_ids += [tokenizer.eos_token_id]
            labels += [tokenizer.eos_token_id]
        total_length = len(input_ids)
        block_size = data_args.cutoff_len
        # 我们去掉小的余数，如果total_length < Block_size，排除这个批次
        total_length = (total_length // block_size) * block_size
        # 按cutoff_len的块分割.
        for i in range(0, total_length, block_size):
            model_inputs["input_ids"].append(input_ids[i: i + block_size])
            model_inputs["attention_mask"].append([1] * block_size)
            model_inputs["labels"].append(labels[i: i + block_size])
        return model_inputs

    def preprocess_unsupervised_dataset(examples: Dict[str, List[Any]]):
        """用于处理无监督数据集.

        它构建输入和标签，处理单轮对话数据，根据需求进行编码、截断和生成适用于模型训练的输入序列和标签序列.
        以`<bos> X`格式构建输入，以`Y <eos>`格式构建标签

        Args:
            examples(Dict[str, List[Any]]): 一个包含了不同键的列表的字典，包含了模型所需的各种数据.

        Returns:
            其中包含处理后的有监督数据集的输入和标签信息: Dict[str, Any]
        """
        model_inputs = {"input_ids": [], "attention_mask": [], "labels": []}
        for query, response, history, system in construct_example(examples):
            # 检查查询是否是字符串且不为空
            if not (isinstance(query, str) and query != ""):
                continue
            # 通过模板的 encode_oneturn 方法将输入序列进行编码，
            # 生成 input_ids（即输入部分）和 labels（即标签部分）.
            input_ids, labels = template.encode_oneturn(
                tokenizer, query, response, history, system)
            # 针对 efficient_eos 的情况进行特殊处理，如果启用了 efficient_eos，则在标签末尾添加结束标记
            if template.efficient_eos:
                labels += [tokenizer.eos_token_id]
            # 根据 data_args.cutoff_len 处理 input_ids 和 labels 的长度.
            if len(input_ids) > data_args.cutoff_len:
                input_ids = input_ids[:data_args.cutoff_len]
            if len(labels) > data_args.cutoff_len:
                labels = labels[:data_args.cutoff_len]
            # 将处理好的 input_ids、attention_mask 和 labels 存储到 model_inputs 字典中.
            model_inputs["input_ids"].append(input_ids)
            model_inputs["attention_mask"].append([1] * len(input_ids))
            model_inputs["labels"].append(labels)
        return model_inputs

    # 处理函数真正开始的地方.
    if not dataset:
        raise ValueError("The dataset does not exist!")
    # 获取对话模板
    template = extras.get_template_and_fix_tokenizer(tokenizer)
    # 在提示符中禁用掩码时不能使用高效结束符
    if data_args.train_on_prompt and template.efficient_eos:
        raise ValueError("Current template does not support `train_on_prompt`.")
    # 选择适当的数据预处理方法.
    if not training_args.predict_with_generate:
        preprocess_func = preprocess_packed_supervised_dataset \
            if data_args.sft_packing else preprocess_supervised_dataset
    else:
        preprocess_func = preprocess_unsupervised_dataset
    # 检查是否提供了缓存路径并且此路径指向一个已存在的文件.
    # 如果是，则返回加载的数据集.
    if data_args.cache_path is not None and os.path.exists(
            data_args.cache_path):
        return load_from_disk(data_args.cache_path)
    # 使用了main_process_first上下文管理器，确保首先在主进程中执行后续的代码.
    with training_args.main_process_first(desc="dataset map pre-processing"):
        # 获取数据集的列名.
        column_names = list(next(iter(dataset)).keys())
        # 初始化空字典用于后续参数设置
        kwargs = {}
        if not data_args.streaming:
            kwargs = dict(
                num_proc=data_args.preprocessing_num_workers,
                load_from_cache_file=not data_args.overwrite_cache,
                desc="Running tokenizer on dataset"
            )
        dataset = dataset.map(
            preprocess_func,
            batched=True,
            remove_columns=column_names,
            **kwargs
        )
        # 如果指定了缓存路径但该路径不存在.
        if data_args.cache_path is not None and not os.path.exists(
                data_args.cache_path):
            # 如果训练参数要求保存数据集，则保存数据集到指定的缓存路径.
            if training_args.should_save:
                dataset.save_to_disk(data_args.cache_path)
            raise SystemExit(
                "Dataset saved, rerun this script with the same --cache_file.")
        return dataset
