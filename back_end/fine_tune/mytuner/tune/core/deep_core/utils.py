#!/usr/bin/env python3.11.2
"""其他处理函数.

Copyright 2023 Zheyun Liu.
License(GPL)
Author: Zheyun Liu.
"""
import torch
from typing import TYPE_CHECKING, Optional
from types import MethodType
if TYPE_CHECKING:
    from transformers.modeling_utils import PreTrainedModel
    from mytuner.hyper_parameter import FinetuningArguments


# 层归一化的名称
LAYERNORM_NAMES = ["norm", "ln_f", "ln_attn", "ln_mlp", "ln_1", "ln_2"]


def find_all_linear_modules(model, output_layer_name="lm_head"):
    """从预训练模型中找到所有的线性（Linear）模块，并返回这些模块的名称列表.

    Args:
        model(PreTrainedModel): 模型.
        output_layer_name(Optional[str]): 输出层名称

    Returns:
        List[str], 即所有线性模块的名称.
    """
    linear_cls = torch.nn.Linear
    module_names = set()
    for name, module in model.named_modules():
        if output_layer_name not in name and isinstance(module, linear_cls):
            module_names.add(name.split(".")[-1])
    if output_layer_name in module_names:
        module_names.remove(output_layer_name)
    return list(module_names)


def prepare_model_for_training(
    model: "PreTrainedModel",
    finetuning_args: "FinetuningArguments",
    output_layer_name: Optional[str] = "lm_head",
    use_gradient_checkpointing: Optional[bool] = True,
):
    """使模型为训练做好准备.

    包括:
        (1)构造fp32中的layernorm
        (2)使输出嵌入层需要梯度
        (3)将lm_head上推到fp32

    Args:
        model(PreTrainedModel): 模型.
        finetuning_args(FinetuningArguments): 微调参数.
        output_layer_name(Optional[str]): 输出层的名字.
        use_gradient_checkpointing(Optional[bool]): 指示是否使用梯度检查点.

    Returns:
        PreTrainedModel的模型.
    """
    # 向上转型fp32中的layernorm权重.
    if finetuning_args.upcast_layernorm:
        for name, param in model.named_parameters():
            if param.ndim == 1 and any(
                    ln_name in name for ln_name in LAYERNORM_NAMES):
                param.data = param.data.to(torch.float32)
    # 指示是否使用梯度检查点.
    # 梯度检查点是一种用于减少内存占用的技术，特别适用于深层神经网络训练，
    # 通过在计算过程中存储部分信息来降低内存需求. 这段代码片段在使用梯度检查点时，
    # 根据模型和设置来配置模型以便进行梯度检查点，并启用了相应的梯度检查点功能.
    if use_gradient_checkpointing:
        if hasattr(model, "enable_input_require_grads"):
            model.enable_input_require_grads()
        else:
            def make_inputs_require_grad(module, input, output):
                """回调函数.

                当模型的输入发生变化时，它将为输出设置requires_grad标志，这样可以追踪梯度信息.

                Arga:
                    module(torch.nn.Module)
                    input(torch.Tensor)
                    output(torch.Tensor)
                """
                output.requires_grad_(True)
            model.get_input_embeddings().register_forward_hook(
                make_inputs_require_grad)
        model.gradient_checkpointing_enable()
        # 启用梯度检查点时关闭.
        model.config.use_cache = False
        # 输出层相关
        if hasattr(model, output_layer_name):
            output_layer = getattr(model, output_layer_name)
            if isinstance(output_layer, torch.nn.Linear):
                def forward_in_fp32(self, x: torch.Tensor) -> torch.Tensor:
                    return output_layer.__class__.forward(self, x.to(
                        output_layer.weight.dtype)).to(torch.float32)
                output_layer.forward = MethodType(forward_in_fp32, output_layer)
    return model

