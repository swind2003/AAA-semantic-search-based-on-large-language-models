#!/usr/bin/env python3.11.2
"""将分词器封装到度量函数中, 用于Seq2SeqPeftTrainer.

Copyright 2023 Zheyun Liu.
License(GPL)
Author: Zheyun Liu.
"""
import numpy as np
from dataclasses import dataclass
from typing import TYPE_CHECKING, Sequence, Tuple, Union

import jieba
from rouge_chinese import Rouge
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction

from mytuner.dataset_processing import IGNORE_INDEX

if TYPE_CHECKING:
    from transformers.tokenization_utils import PreTrainedTokenizer


@dataclass
class ComputeMetrics:
    """将分词器封装成度量函数，用于Seq2SeqPeftTrainer.

    Attributes:
        tokenizer (PreTrainedTokenizer): 分词器.
    """
    tokenizer: "PreTrainedTokenizer"

    def __call__(
            self,
            eval_preds: Sequence[Union[np.ndarray, Tuple[np.ndarray]]]
    ):
        """使用模型预测结果来计算度量指标.

        Args:
            eval_preds (Sequence[Union[np.ndarray, Tuple[np.ndarray]]]):
                一个序列, 包含模型预测的结果和对应的标签.

        Returns:
            返回一个Dict[str, float]类型字典，包含不同度量指标
            （如 Rouge-1、Rouge-2、Rouge-L 和 BLEU-4）的得分.
        """
        # 解包为 preds 和 labels.
        preds, labels = eval_preds
        # score_dict 用于存储各种指标的分数.
        score_dict = {
            "rouge-1": [],
            "rouge-2": [],
            "rouge-l": [],
            "bleu-4": []
        }
        # 对 preds 和 labels 使用 np.where 函数，
        # 将其中等于特定索引（在这里是 IGNORE_INDEX）的值替换为分词器的填充标记.
        preds = np.where(
            preds != IGNORE_INDEX,
            preds,
            self.tokenizer.pad_token_id
        )
        labels = np.where(
            labels != IGNORE_INDEX,
            labels,
            self.tokenizer.pad_token_id
        )
        # 使用分词器 tokenizer 的 batch_decode 方法，
        # 将预测和标签解码为人类可读的文本格式，跳过特殊标记.
        decoded_preds = self.tokenizer.batch_decode(
            preds,
            skip_special_tokens=True
        )
        decoded_labels = self.tokenizer.batch_decode(
            labels,
            skip_special_tokens=True
        )
        for pred, label in zip(decoded_preds, decoded_labels):
            # 将预测值和标签值进行分词（使用 jieba.cut）,
            # 得到假设（hypothesis）和参考（reference）.
            # 假设为预测值分词后的结果.
            hypothesis = list(jieba.cut(pred))
            # 参考为标签值分词后的结果.
            reference = list(jieba.cut(label))
            # 检查分词结果是否为空，如果为空，则设定默认的 Rouge 分数为 0.0.
            if (len(" ".join(hypothesis).split()) == 0 or
                    len(" ".join(reference).split()) == 0):
                result = {
                    "rouge-1": {"f": 0.0},
                    "rouge-2": {"f": 0.0},
                    "rouge-l": {"f": 0.0}
                }
            else:
                # 创建 Rouge 实例.
                rouge = Rouge()
                scores = rouge.get_scores(
                    " ".join(hypothesis),
                    " ".join(reference)
                )
                result = scores[0]
            # 将计算出的 Rouge 和 BLEU 分数存储到 score_dict 中
            for k, v in result.items():
                score_dict[k].append(round(v["f"] * 100, 4))
            # 计算 BLEU-4 分数并存入指标字典中.
            bleu_score = sentence_bleu(
                [list(label)],
                list(pred),
                smoothing_function=SmoothingFunction().method3
            )
            score_dict["bleu-4"].append(round(bleu_score * 100, 4))
        # 计算各指标的平均值并返回.
        return {k: float(np.mean(v)) for k, v in score_dict.items()}
