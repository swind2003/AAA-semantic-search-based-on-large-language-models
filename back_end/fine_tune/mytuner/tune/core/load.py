#!/usr/bin/env python3.11.2
"""加载模型和令牌.

Copyright 2023 Zheyun Liu.
License(GPL)
Author: Zheyun Liu.
"""
import torch
from types import MethodType
from typing import TYPE_CHECKING
from transformers import (
    AutoConfig,
    AutoModelForCausalLM,
    AutoTokenizer,
    PretrainedConfig,
    PreTrainedModel,
    PreTrainedTokenizerBase
)
try:
    from transformers.utils import (
        is_torch_bf16_cpu_available,
        is_torch_bf16_gpu_available,
        is_torch_cuda_available,
        is_torch_npu_available
    )
    _is_fp16_available = is_torch_npu_available() or is_torch_cuda_available()
    _is_bf16_available = (
            is_torch_bf16_gpu_available() or is_torch_bf16_cpu_available)
except ImportError:
    _is_fp16_available = torch.cuda.is_available()
    _is_bf16_available = torch.cuda.is_bf16_supported()
from mytuner.hyper_parameter import FinetuningArguments
from mytuner.tune.core import deep_core

if TYPE_CHECKING:
    from mytuner.hyper_parameter import ModelArguments


def infer_optim_dtype(model_dtype):
    """根据model_dtype和设备兼容性推断最佳dtype.

    Args:
        model_dtype(torch.dtype): 模型数据类型.

    Returns:
        torch.dtype
    """
    if _is_bf16_available and model_dtype == torch.bfloat16:
        return torch.bfloat16
    elif _is_fp16_available:
        return torch.float16
    else:
        return torch.float32


def load_model_and_tokenizer(model_args, finetuning_args, is_trainable=False):
    """加载模型和令牌的函数.

    Args:
        model_args(ModelArguments): 模型参数
        finetuning_args(FinetuningArguments): 微调参数
        is_trainable(bool): 是否可训练

    Returns:
        Tuple[PreTrainedModel, PreTrainedTokenizer]
    """
    config_kwargs = {
        "trust_remote_code": True,
        "revision": model_args.model_revision,
        "use_auth_token": None,
    }
    tokenizer = AutoTokenizer.from_pretrained(
        model_args.model_name_or_path,
        use_fast=model_args.use_fast_tokenizer,
        split_special_tokens=model_args.split_special_tokens,
        padding_side="right",
        **config_kwargs
    )
    model_to_load = model_args.model_name_or_path
    config = AutoConfig.from_pretrained(model_to_load, **config_kwargs)
    # 修复令牌 (ChatGLM2 和 ChatGLM3 独有)
    # 这行代码的效果是将_pad属性重新定义为PreTrainedTokenizerBase类中_pad方法的一个新实例，
    # 并将tokenizer对象作为该方法的第一个参数，这样可以确保在访问_pad属性时，会调用
    # PreTrainedTokenizerBase类中的_pad方法，并以tokenizer对象作为第一个参数进行处理.
    tokenizer._pad = MethodType(PreTrainedTokenizerBase._pad, tokenizer)
    # 设置模型数据类型
    if model_args.compute_dtype is not None:
        setattr(config, "torch_dtype", model_args.compute_dtype)
    else:
        model_args.compute_dtype = infer_optim_dtype(
            model_dtype=getattr(config, "torch_dtype", None))
    # 加载和准备预训练模型(没有valuehead).
    model = AutoModelForCausalLM.from_pretrained(
        model_to_load,
        config=config,
        torch_dtype=model_args.compute_dtype,
        low_cpu_mem_usage=True,
        **config_kwargs
    )
    # 修改 LM head (ChatGLM2 和 ChatGLM3 独有)
    setattr(model, "lm_head", model.transformer.output_layer)
    # 注册自动类以保存自定义代码文件.
    # 这段代码的作用是根据给定条件，将特定的自动类注册到相应的对象中，以在保存自定义代码文件时使用.
    if (isinstance(config, PretrainedConfig)
            and "AutoConfig" in getattr(config, "auto_map", {})):
        config.__class__.register_for_auto_class()
    if (isinstance(model, PreTrainedModel)
            and "AutoModelForCausalLM" in getattr(config, "auto_map", {})):
        model.__class__.register_for_auto_class()
    if (isinstance(tokenizer, PreTrainedTokenizerBase)
            and "AutoTokenizer" in tokenizer.init_kwargs.get("auto_map", {})):
        tokenizer.__class__.register_for_auto_class()
    # 初始化适配器
    model = deep_core.prepare_model_for_training(
        model=model, finetuning_args=finetuning_args) if is_trainable else model
    model = deep_core.init_adapter(
        model, model_args, finetuning_args, is_trainable, True)
    model = model.train() if is_trainable else model.eval()
    # 如果是为推理准备模型.
    if not is_trainable:
        # 修改所有模型参数.
        model.requires_grad_(False)
        model = model.to(model_args.compute_dtype)
    return model, tokenizer
