#!/usr/bin/env python3.11.2
"""解码参数.

Copyright 2023 Zheyun Liu.
License(GPL)
Author: Zheyun Liu.
"""
from typing import Optional
from dataclasses import asdict, dataclass, field


@dataclass
class GeneratingArguments:
    """用于指定解码参数.

    Attributes:
        do_sample(Optional[bool]): 是否使用采样, 不用则使用贪婪解码.
        temperature(Optional[float]): 用于调制下一个标记概率的值, 就是我们熟知的模型的温度.
        top_p(Optional[float]): 保留概率加起来大于或等于top_p的最可能标记的最小集合.
        top_k(Optional[int]): 要为top-k过滤保留的最高概率词汇表标记的数量.
        num_beams(Optional[int]): 波束搜索的波束数. 1表示无波束搜索.
        max_length(Optional[int]): 生成的token的最大长度. 它可以由max_new_tokens覆盖.
        max_new_tokens(Optional[int]): 要生成的最大标记数. 忽略提示符中的标记数.
        repetition_penalty(Optional[float]): 重复惩罚的参数. 1.0意味着没有惩罚.
        length_penalty(Optional[float]): 对基于波束的生成所使用的长度的指数惩罚.
    """
    do_sample: Optional[bool] = field(
        default=True,
        metadata={
            "help": "Whether or not to use sampling, "
                    "use greedy decoding otherwise."}
    )
    temperature: Optional[float] = field(
        default=0.95,
        metadata={
            "help": "The value used to modulate the next token probabilities."}
    )
    top_p: Optional[float] = field(
        default=0.7,
        metadata={
            "help": "The smallest set of most probable tokens with "
                    "probabilities that add up to top_p or higher are kept."}
    )
    top_k: Optional[int] = field(
        default=50,
        metadata={
            "help": "The number of highest probability vocabulary tokens "
                    "to keep for top-k filtering."}
    )
    num_beams: Optional[int] = field(
        default=1,
        metadata={
            "help": "Number of beams for beam search. 1 means no beam search."}
    )
    max_length: Optional[int] = field(
        default=None,
        metadata={
            "help": "The maximum length the generated tokens can have. "
                    "It can be overridden by max_new_tokens."}
    )
    max_new_tokens: Optional[int] = field(
        default=512,
        metadata={
            "help": "The maximum numbers of tokens to generate, "
                    "ignoring the number of tokens in the prompt."}
    )
    repetition_penalty: Optional[float] = field(
        default=1.0,
        metadata={
            "help": "The parameter for repetition penalty. "
                    "1.0 means no penalty."}
    )
    length_penalty: Optional[float] = field(
        default=1.0,
        metadata={
            "help": "Exponential penalty to the length that is used "
                    "with beam-based generation."}
    )

    def to_dict(self):
        """将自身的参数转化为字典形式保存.

        Returns:
            Dict[str, Any]格式的参数.
        """
        args = asdict(self)
        if args.get("max_new_tokens", None):
            args.pop("max_length", None)
        return args
