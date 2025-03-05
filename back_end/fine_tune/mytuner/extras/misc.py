#!/usr/bin/env python3.11.2
"""这里的代码涵盖了一系列辅助函数和操作.

Copyright 2023 Zheyun Liu.
License(GPL)
Author: Zheyun Liu.
"""
import torch
from transformers import InfNanRemoveLogitsProcessor, LogitsProcessorList
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from transformers.modeling_utils import PreTrainedModel


def get_logits_processor():
    """返回一个处理 logits 的处理器列表，用于移除 NaN 和 Inf 的 logits.

    Returns:
        LogitsProcessorList
    """
    logits_processor = LogitsProcessorList()
    logits_processor.append(InfNanRemoveLogitsProcessor())
    return logits_processor


def dispatch_model(model: "PreTrainedModel"):
    """将预训练模型分发到内存平衡的gpu.

    借用: https://github.com/huggingface/transformers/blob/v4.31.0/src/transformers/modeling_utils.py#L2803

    Args:
        model (PreTrainedModel): 一个PreTrainedModel类型的模型.

    Returns:
        处理过后的PreTrainedModel类型的模型: PreTrainedModel
    """
    # 如果当前CUDA设备的数量大于1，则使用accelerate库进行操作.
    if torch.cuda.device_count() > 1:
        from accelerate import dispatch_model
        from accelerate.utils import infer_auto_device_map, get_balanced_memory
        # 检查模型的属性_no_split_modules是否为None. 如果是None，则会抛出ValueError错误.
        if model._no_split_modules is None:
            raise ValueError("The model class needs to implement the "
                             "`_no_split_modules` attribute.")
        # 创建一个kwargs字典，其中包含了模型的数据类型（dtype）和不应该分割的模块类列表
        # （no_split_module_classes），这些信息将被用于后续的操作.
        kwargs = {
            "dtype": model.dtype,
            "no_split_module_classes": model._no_split_modules
        }
        # 使用get_balanced_memory函数计算了一个最大内存值max_memory，
        # 这个函数估计了模型在多GPU上平衡内存使用的方式.
        max_memory = get_balanced_memory(model, **kwargs)
        # 在创建设备映射之前，确保权重是绑定的.
        model.tie_weights()
        # 根据模型的特性和最大内存值生成一个自动设备映射.
        device_map = infer_auto_device_map(
            model,
            max_memory=max_memory,
            **kwargs
        )
        # 调用dispatch_model函数，并将模型和设备映射作为参数传递，进一步分发模型到多个GPU上.
        return dispatch_model(model, device_map)
    else:
        # 如果当前CUDA设备数量不大于1，则直接将模型移到GPU上并返回.
        return model.cuda()
