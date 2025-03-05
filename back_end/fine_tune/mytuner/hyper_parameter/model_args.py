#!/usr/bin/env python3.11.2
"""存放模型相关参数的数据类型.

Copyright 2023 Zheyun Liu.
License(GPL)
Author: Zheyun Liu.
"""
from typing import Optional
from dataclasses import dataclass, field


@dataclass
class ModelArguments:
    """与我们要微调的model/config/tokenizer相关的参数.

    用于存储和管理模型相关的参数.
    这些参数用于微调（fine-tuning）模型、配置模型、和标记器（tokenizer）.

    Args:
        model_name_or_path(str): 预训练模型的路径.
        use_fast_tokenizer(Optional[bool]): 是否使用快速分词器(由分词器库支持).
            快速标记器是基于 tokenizers 库构建的，它们通常比慢速标记器更快速，并提供更好的性能.
            特别是在处理大型文本数据时.这些快速标记器能够更高效地进行分词和标记化.
        split_special_tokens(Optional[bool]): 在分词过程中是否拆分特殊标记.
            特殊标记是指在自然语言处理任务中具有特殊含义或功能的标记，比如句子的起始和结束标记、
            掩码标记、分隔标记等。在某些情况下，可能需要对这些特殊标记进行处理.
            当 split_special_tokens 被设置为 True 时，系统会将特殊标记进行拆分.
            这意味着这些特殊标记将被分解成单独的标记，而不是作为一个整体被视为一个单一的标记.
            这种拆分可以影响标记化的结果，尤其是在某些特定任务中可能需要对特殊标记进行更细粒度的处理时.
            并非所有的标记器都支持对特殊标记进行拆分，因此在设置split_special_tokens为True时
            会检查所使用的标记器是否支持这种操作.在一些情况下，使用快速的标记器
            （backed by the tokenizers 库）可能不支持对特殊标记的拆分，
            所以在此情况下会引发 ValueError.
        model_revision(Optional[str]): 要使用的具体模型版本(可以是分支名称、标签名称或提交id).
        checkpoint_dir(Optional[str]): 包含增量模型检查点和配置的目录的路径.
        export_dir(Optional[str]): 保存导出模型的路径.
    """
    model_name_or_path: str = field(
        metadata={"help": "Path to pretrained model"}
    )
    use_fast_tokenizer: Optional[bool] = field(
        default=True,
        metadata={
            "help": "Whether to use one of the fast tokenizer "
                    "(backed by the tokenizers library) or not."}
    )
    split_special_tokens: Optional[bool] = field(
        default=False,
        metadata={
            "help": "Whether or not the special tokens should be split "
                    "during the tokenization process."}
    )
    model_revision: Optional[str] = field(
        default="main",
        metadata={
            "help": "The specific model version to use "
                    "(can be a branch name, tag name or commit id)."}
    )
    checkpoint_dir: Optional[str] = field(
        default=None,
        metadata={
            "help": "Path to the directory(s) containing the delta model "
                    "checkpoints as well as the configurations."}
    )
    export_dir: Optional[str] = field(
        default=None,
        metadata={"help": "Path to the directory to save the exported model."}
    )

    def __post_init__(self):
        """在类的实例初始化之后进行额外的初始化操作.

        1.首先对两个额外的属性 compute_dtype 和 model_max_length 进行了None值初始化.
        2.验证了是否同时启用了 split_special_tokens 和 use_fast_tokenizer 参数，
        如果是，则抛出 ValueError 异常，因为这两个参数是不兼容的.
        3.检查是否设置了 checkpoint_dir，如果设置了，则将其值分割成一个列表.
        4.验证了 quantization_bit 参数是否在可接受的范围内.

        """
        self.compute_dtype = None
        self.model_max_length = None
        # 验证了是否同时启用了 split_special_tokens 和 use_fast_tokenizer 参数.
        if self.split_special_tokens and self.use_fast_tokenizer:
            raise ValueError(
                "`split_special_tokens` is only supported for slow tokenizers.")
        # 支持合并多个lora权重
        if self.checkpoint_dir is not None:
            self.checkpoint_dir = \
                [cd.strip() for cd in self.checkpoint_dir.split(",")]
