#!/usr/bin/env python3.11.2
"""初始化适配器.

Copyright 2023 Zheyun Liu.
License(GPL)
Author: Zheyun Liu.
"""
from typing import TYPE_CHECKING
# PEFT旨在通过在模型训练过程中部分执行（Partial Execution）来提高训练效率和性能
from peft import (
    PeftModel,
    TaskType,
    LoraConfig,
    get_peft_model
)
from mytuner.tune.core.deep_core import utils
if TYPE_CHECKING:
    from transformers.modeling_utils import PreTrainedModel
    from mytuner.hyper_parameter import ModelArguments, FinetuningArguments


def init_adapter(
    model,
    model_args,
    finetuning_args,
    is_trainable,
    is_mergeable
):
    """初始化适配器.

    注意，可训练参数必须转换为float32类型.

    Args:
        model(PreTrainedModel): 模型.
        model_args(ModelArguments): 模型参数.
        finetuning_args(FinetuningArguments): 微调参数.
        is_trainable(bool): 判断是否在训练中.
        is_mergeable(bool): 是否合并.

    Returns:
        PreTrainedModel类型的处理后模型
    """
    latest_checkpoint = None
    # 如果存在最新的检查点，则从最新的检查点中加载模型.
    if model_args.checkpoint_dir is not None:
        if ((is_trainable and finetuning_args.resume_lora_training) or
                (not is_mergeable)):
            checkpoints_to_merge, latest_checkpoint = (
                model_args.checkpoint_dir[:-1], model_args.checkpoint_dir[-1])
        else:
            checkpoints_to_merge = model_args.checkpoint_dir
        for checkpoint in checkpoints_to_merge:
            model = PeftModel.from_pretrained(model, checkpoint)
            model = model.merge_and_unload()
        #  恢复lora训练或量化推理.
        if latest_checkpoint is not None:
            model = PeftModel.from_pretrained(model, latest_checkpoint,
                                              is_trainable=is_trainable)
    # 如果处于训练状态且没有最新的检查点, 训练时创建新的lora权重.
    if is_trainable and latest_checkpoint is None:
        if len(finetuning_args.lora_target) == 1 and \
                finetuning_args.lora_target[0] == "all":
            target_modules = utils.find_all_linear_modules(model)
        else:
            target_modules = finetuning_args.lora_target
        lora_config = LoraConfig(
            task_type=TaskType.CAUSAL_LM,
            inference_mode=False,
            r=finetuning_args.lora_rank,
            lora_alpha=int(finetuning_args.lora_alpha),
            lora_dropout=finetuning_args.lora_dropout,
            target_modules=target_modules,
            modules_to_save=finetuning_args.additional_target
        )
        model = get_peft_model(model, lora_config)
        if id(model.peft_config) != id(
                model.base_model.peft_config):
            model.base_model.peft_config = model.peft_config
    return model
