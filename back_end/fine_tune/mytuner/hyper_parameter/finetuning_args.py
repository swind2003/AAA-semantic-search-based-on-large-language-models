#!/usr/bin/env python3.11.2
"""存放模型微调参数的数据类型.

Copyright 2023 Zheyun Liu.
License(GPL)
Author: Zheyun Liu.
"""
import json
from typing import Literal, Optional
from dataclasses import asdict, dataclass, field


@dataclass
class FinetuningArguments:
    """使用哪些技术进行微调.

    Attributes:
        num_layer_trainable(Optional[int]): 用于部分参数(冻结)微调的可训练层数.
        name_module_trainable(Optional[Literal['mlp', 'self_attention']]):
            用于部分参数(冻结)微调的可训练模块的名称.
        lora_rank(Optional[int]): LoRA微调的内在维度.
        lora_alpha(float): LoRA微调的比例因子(类似于学习率).
        lora_dropout(Optional[float]): LoRA微调的dropout率.
        lora_target(Optional[str]): 应用LoRA的目标模块的名称. 使用逗号分隔多个模块.
        additional_target(Optional[str]):
            除了LoRA层之外被设置为可训练并保存在最后的检查点的模块名称.
        resume_lora_training(Optional[bool]):
            是从最后一个LoRA权重恢复训练还是在合并它们后创建新的权重.
        upcast_layernorm(Optional[bool]): 是否向上转型fp32中的layernorm权重.
    """
    num_layer_trainable: Optional[int] = field(
        default=3,
        metadata={"help": "Number of trainable layers for partial-parameter "
                          "(freeze) fine-tuning."}
    )
    name_module_trainable: Optional[Literal["mlp", "self_attention"]] = field(
        default="mlp",
        metadata={"help": "Name of trainable modules for partial-parameter "
                          "(freeze) fine-tuning."}
    )
    lora_rank: Optional[int] = field(
        default=8,
        metadata={"help": "The intrinsic dimension for LoRA fine-tuning."}
    )
    lora_alpha: float = field(
        default=32.0,
        metadata={"help": "The scale factor for LoRA fine-tuning "
                          "(similar with the learning rate)."}
    )
    lora_dropout: Optional[float] = field(
        default=0.1,
        metadata={"help": "Dropout rate for the LoRA fine-tuning."}
    )
    lora_target: Optional[str] = field(
        default=None,
        metadata={"help": "Name(s) of target modules to apply LoRA. "
                          "Use commas to separate multiple modules. "
                          "ChatGLM choices: ['query_key_value',"
                          " 'self_attention.dense', 'mlp.dense']"}
    )
    additional_target: Optional[str] = field(
        default=None,
        metadata={"help": "Name(s) of modules apart from LoRA layers to be set"
                          " as trainable and saved in the final checkpoint."}
    )
    resume_lora_training: Optional[bool] = field(
        default=True,
        metadata={"help": "Whether to resume training from the last LoRA "
                          "weights or create new weights after merging them."}
    )
    upcast_layernorm: Optional[bool] = field(
        default=False,
        metadata={"help": "Whether to upcast the layernorm weights in fp32."}
    )

    def __post_init__(self):
        """在类的实例初始化之后进行额外的初始化操作.

        将 self.lora_target 和 self.additional_target 字段的值转换为列表.
        如果它们最初是字符串形式（由于从 JSON 中加载时可能是字符串），
        则通过将其拆分为逗号分隔的值，创建对应的列表.
        """
        if isinstance(self.lora_target, str):
            self.lora_target = [target.strip() for target
                                in self.lora_target.split(",")]
        if isinstance(self.additional_target, str):
            self.additional_target = [target.strip() for target
                                      in self.additional_target.split(",")]

    def save_to_json(self, json_path):
        """这个方法用于将类的实例内容以 JSON 格式保存到指定路径的文件中.

        asdict()将数据类的实例转换为一个字典.
        通过调用 json.dumps() 将字典转换为 JSON 字符串，
        然后将该字符串写入到指定路径的文件中.

        Args:
            json_path(str): 指定路径的文件
        """
        json_string = json.dumps(asdict(self), indent=2, sort_keys=True) + "\n"
        with open(json_path, "w", encoding="utf-8") as f:
            f.write(json_string)

    @classmethod
    def load_from_json(cls, json_path: str):
        """从 JSON 文件中加载数据并创建类的实例.

        它首先打开指定路径的 JSON 文件，读取文件内容，然后通过调用 json.loads()
        将 JSON 字符串转换为 Python 字典.
        最后，使用类的构造函数 cls()（即类方法的第一个参数，代表类本身）
        以及从 JSON 文件加载的字典内容，创建并返回一个类的实例.
        """
        with open(json_path, "r", encoding="utf-8") as f:
            text = f.read()
        # json.loads(text) 解析 JSON 字符串并将其转换为字典.
        # 然后 cls(**json.loads(text)) 转化字典为关键字参数创建了一个类 cls 的实例.
        return cls(**json.loads(text))
