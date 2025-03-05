#!/usr/bin/env python3.11.2
"""此文件下的函数用于解析参数.

Copyright 2023 Zheyun Liu.
License(GPL)
Author: Zheyun Liu.
"""
import os
import sys
import torch
import transformers
from transformers import HfArgumentParser, Seq2SeqTrainingArguments
from transformers.trainer_utils import get_last_checkpoint
from mytuner.hyper_parameter import (
    ModelArguments,
    DataArguments,
    FinetuningArguments,
    GeneratingArguments
)


def _parse_args(parser, args=None):
    """将参数解析为指定dataclass类型的实例.

    HfArgumentParser的实现信息参考自huggingface官网.

    Args:
        parser(HfArgumentParser): HfArgumentParser类型的参数解析器,封装了对应
            dataclass类型的实例.
        args(Optional[Dict[str, Any]]): 传入的参数，可以是通过字典传入的，也可以是None，
            以字典格式传入的参数key为str类型，值为任意类型.

    Returns:
        Tuple[Any]类型的解析后的参数.
    """
    # 如果是通过字典传入参数，调用HfArgumentParser的parse_dict解析参数.
    if args is not None:
        return parser.parse_dict(args)
    # 如果是通过.yaml传入参数，调用HfArgumentParser的parse_yaml_file函数解析参数.
    elif len(sys.argv) == 2 and sys.argv[1].endswith(".yaml"):
        return parser.parse_yaml_file(os.path.abspath(sys.argv[1]))
    # 如果是通过.json传入参数，调用HfArgumentParser的parse_json_file函数解析参数.
    elif len(sys.argv) == 2 and sys.argv[1].endswith(".json"):
        return parser.parse_json_file(os.path.abspath(sys.argv[1]))
    # 如果是通过命令行传入参数，调用HfArgumentParser的相应函数解析参数.
    else:
        return parser.parse_args_into_dataclasses()


def get_train_args(args=None):
    """获得解析后的训练参数.

    Args:
        args (Optional[Dict[str, Any]]): 关键字参数.

    Returns:
        Tuple[
            ModelArguments,
            DataArguments,
            Seq2SeqTrainingArguments,
            FinetuningArguments,
            GeneratingArguments
        ]
    """
    parser = HfArgumentParser((
        ModelArguments,
        DataArguments,
        Seq2SeqTrainingArguments,
        FinetuningArguments,
        GeneratingArguments
    ))
    model_args, data_args, training_args, finetuning_args, generating_args = (
        _parse_args(parser, args))
    # 初始化数据集参数.
    data_args.init_for_training(training_args.seed)
    # 处理training_args(Seq2SeqTrainingArguments类型).
    # Seq2SeqTrainingArguments来自Huggingface的tranformer库
    # 检查ddp_find_unused_parameters是否设置为了False.
    # 如果使用梯度检查点为False，否则为True.
    if (
        training_args.local_rank != -1
        and training_args.ddp_find_unused_parameters is None
    ):
        training_args_dict = training_args.to_dict()
        training_args_dict.update(dict(ddp_find_unused_parameters=False))
        training_args = Seq2SeqTrainingArguments(**training_args_dict)
    if (
        training_args.resume_from_checkpoint is None
        and training_args.do_train
        and os.path.isdir(training_args.output_dir)
        and not training_args.overwrite_output_dir
    ):
        last_checkpoint = get_last_checkpoint(training_args.output_dir)
        # 输出路径不为空，但却未设置resume_from_checkpoint和overwrite_output_dir
        if last_checkpoint is None and len(
                os.listdir(training_args.output_dir)) > 0:
            raise ValueError("Output directory already exists and is not empty."
                             " Please set `overwrite_output_dir`.")
        # 找到了last_checkpoint, 自动设置为resume_from_checkpoint, 继续训练
        if last_checkpoint is not None:
            training_args_dict = training_args.to_dict()
            training_args_dict.update(
                dict(resume_from_checkpoint=last_checkpoint))
            training_args = Seq2SeqTrainingArguments(**training_args_dict)
    # 处理model_args
    model_args.compute_dtype = (
        torch.bfloat16 if training_args.bf16
        else (torch.float16 if training_args.fp16 else None)
    )
    model_args.model_max_length = data_args.cutoff_len
    # 在初始化模型之前设置种子.
    transformers.set_seed(training_args.seed)
    return (
        model_args,
        data_args,
        training_args,
        finetuning_args,
        generating_args
    )


def get_infer_args(args=None):
    """根据参数返回一组推断所需的模型参数、数据参数、微调参数和生成参数.

    Args:
        args (Optional[Dict[str, Any]]): 关键字参数.

    Returns:
        Tuple[
            ModelArguments,
            DataArguments,
            FinetuningArguments,
            GeneratingArguments
        ]
    """
    parser = HfArgumentParser((
        ModelArguments,
        DataArguments,
        FinetuningArguments,
        GeneratingArguments
    ))
    model_args, data_args, finetuning_args, generating_args = (
        _parse_args(parser, args))
    return model_args, data_args, finetuning_args, generating_args
