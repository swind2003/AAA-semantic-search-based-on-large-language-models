#!/usr/bin/env python3.11.2
"""训练器文件.

Copyright 2023 Zheyun Liu.
License(GPL)
Author: Zheyun Liu.
"""
import os
import json
import torch
import numpy as np
import torch.nn as nn
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union
from transformers import Seq2SeqTrainer
from mytuner.dataset_processing import IGNORE_INDEX
if TYPE_CHECKING:
    from transformers.trainer import PredictionOutput


class CustomSeq2SeqTrainer(Seq2SeqTrainer):
    """CustomSeq2SeqTrainer类继承自Seq2SeqTrainer类.

    用于定制序列到序列（Seq2Seq）训练器，扩展其功能以计算生成式任务的指标（例如BLEU和ROUGE）.
    """
    def prediction_step(
        self,
        model: nn.Module,
        inputs: Dict[str, Union[torch.Tensor, Any]],
        prediction_loss_only: bool,
        ignore_keys: Optional[List[str]] = None,
    ):
        """重写了Seq2SeqTrainer的prediction_step方法.

        用于处理模型的预测步骤.
        删除了生成的标记中的提示部分，并确保模型生成的输出与输入的长度相匹配.
        通过调用super().prediction_step()来执行基类方法，获取损失值、生成的标记以及标签信息.

        Args:
            model (nn.Module): 模型.
            inputs (Dict[str, Union[torch.Tensor, Any]]): 输入.
            prediction_loss_only (bool): 指示是否仅返回损失值.
            ignore_keys (Optional[List[str]]): 指定要忽略的键的列表.

        Returns:
            一个元组，包含损失值、生成的标记和标签的张量:
            Tuple[
                Optional[float],
                Optional[torch.Tensor],
                Optional[torch.Tensor]
            ]
        """
        # 备份了输入数据中的标签信息
        labels = inputs["labels"].clone() if "labels" in inputs else None
        # 如果需要进行生成式预测, 则对输入的预测和标签进行处理以匹配长度.
        if self.args.predict_with_generate:
            assert self.tokenizer.padding_side == "left", \
                "This method only accepts left-padded tensor."
            prompt_len, label_len = (
                inputs["input_ids"].size(-1), inputs["labels"].size(-1))
            # 确保模型输入 input_ids 的长度等于或大于标签 labels 的长度，并进行必要的填充或截断操作.
            if prompt_len > label_len:
                inputs["labels"] = self._pad_tensors_to_target_len(
                    inputs["labels"],
                    inputs["input_ids"]
                )
            if label_len > prompt_len:
                inputs["labels"] = inputs["labels"][:, :prompt_len]
        else:
            prompt_len = 0
        # 通过super().prediction_step()调用了基类Seq2SeqTrainer中的prediction_step方法,
        # 执行模型预测, 获取了损失值loss、生成的标记generated_tokens和标签信息.
        loss, generated_tokens, _ = super().prediction_step(
            model,
            inputs,
            prediction_loss_only=prediction_loss_only,
            ignore_keys=ignore_keys
        )
        # 对生成的标记进行处理，确保生成的标记长度与输入的提示部分相匹配，并在需要时进行填充。
        if generated_tokens is not None and self.args.predict_with_generate:
            # 将生成的标记中与提示部分对应的部分设置为填充标记，以确保输出符合期望的长度.
            generated_tokens[:, :prompt_len] = self.tokenizer.pad_token_id
            generated_tokens = generated_tokens.contiguous()
        return loss, generated_tokens, labels

    def _pad_tensors_to_target_len(
        self,
        src_tensor: torch.Tensor,
        tgt_tensor: torch.Tensor
    ):
        """用于对源张量进行填充，使其长度与目标张量相匹配.

        Args:
            src_tensor (torch.Tensor): 需要进行填充的源张量.
            tgt_tensor (torch.Tensor): 目标张量，用于指示源张量需要填充到的目标长度.

        Returns:
            填充后的源张量: torch.Tensor
        """
        # 确保填充标记self.tokenizer.pad_token_id是有效的，如果不是则会触发异常.
        assert self.tokenizer.pad_token_id is not None, "Pad token is required."
        # 创建了一个全零张量 padded_tensor，形状与 tgt_tensor 相同，用填充标记进行填充.
        padded_tensor = self.tokenizer.pad_token_id * torch.ones_like(tgt_tensor)
        # 通过将源张量的值赋给 padded_tensor 的适当部分来进行填充.
        # 这里假定源张量是左填充的，因此在padded_tensor中，源张量应当放置在目标张量的右侧，
        # 如果源张量比目标张量长，只保留源张量的右侧部分.
        padded_tensor[:, -src_tensor.shape[-1]:] = src_tensor
        return padded_tensor.contiguous()

    def save_predictions(
        self,
        predict_results: "PredictionOutput"
    ) -> None:
        """保存模型的预测结果到文件.

        Args:
            predict_results (PredictionOutput): 包含模型预测结果的对象.
        """
        # 检查当前进程是否是主进程，如果不是则不执行后续操作，这样可以确保只有主进程保存预测结果.
        if not self.is_world_process_zero():
            return
        # 构造了一个输出文件的路径 output_prediction_file，用于存储生成的预测结果的文件名.
        output_prediction_file = os.path.join(
            self.args.output_dir,
            "generated_predictions.jsonl"
        )
        # 对预测结果中的预测和标签张量进行处理，将其中的特定索引（IGNORE_INDEX）替换为分词器的填充标记.
        preds = np.where(
            predict_results.predictions != IGNORE_INDEX,
            predict_results.predictions,
            self.tokenizer.pad_token_id
        )
        labels = np.where(
            predict_results.label_ids != IGNORE_INDEX,
            predict_results.label_ids,
            self.tokenizer.pad_token_id
        )
        # 使用分词器的 batch_decode 方法将处理后的预测和标签张量转换为人类可读的文本形式.
        decoded_preds = self.tokenizer.batch_decode(
            preds,
            skip_special_tokens=True,
            clean_up_tokenization_spaces=True
        )
        decoded_labels = self.tokenizer.batch_decode(
            labels,
            skip_special_tokens=True,
            clean_up_tokenization_spaces=True
        )
        # 将转换后的预测和标签以 JSON Lines 的格式（每行一个 JSON 对象）写入到输出文件中.
        with open(output_prediction_file, "w", encoding="utf-8") as writer:
            res: List[str] = []
            for pred, label in zip(decoded_preds, decoded_labels):
                res.append(
                    json.dumps(
                        {
                            "label": label,
                            "predict": pred
                        },
                        ensure_ascii=False
                    )
                )
            writer.write("\n".join(res))
