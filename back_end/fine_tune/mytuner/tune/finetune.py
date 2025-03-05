#!/usr/bin/env python3.11.2
"""这里的函数实现了指令监督微调.

Copyright 2023 Zheyun Liu.
License(GPL)
Author: Zheyun Liu.
"""
from typing import TYPE_CHECKING
from transformers import DataCollatorForSeq2Seq, Seq2SeqTrainingArguments
from mytuner import dataset_processing
from mytuner.tune import core
from mytuner import extras

if TYPE_CHECKING:
    from mytuner.hyper_parameter import (
        ModelArguments,
        DataArguments,
        FinetuningArguments,
        GeneratingArguments
    )


def supervise_fine_tuning(
        model_args, data_args, training_args, finetuning_args, generating_args):
    """指令监督微调的实现代码.

    Args:
        model_args(ModelArguments): 模型参数
        data_args(DataArguments): 数据参数
        training_args(Seq2SeqTrainingArguments): 训练参数
        finetuning_args(FinetuningArguments): 微调参数
        generating_args(GeneratingArguments): 解码参数
    """
    # 获取数据集
    dataset = dataset_processing.get_dataset(data_args)
    # 获取模型和令牌生成器
    model, tokenizer = core.load_model_and_tokenizer(
        model_args, finetuning_args, training_args.do_train
    )
    # 预处理数据集
    dataset = dataset_processing.preprocess_dataset(
        dataset, tokenizer, data_args, training_args
    )
    # 模型在训练过程中会执行生成任务, 但默认是预测任务
    if training_args.predict_with_generate:
        # 在代码中使用左填充, 这个值默认是右填充.
        tokenizer.padding_side = "left"
    # 为序列到序列的任务准备模型训练所需的数据，并在必要时对输入序列和标签进行填充，以便将它们整理成适当的批次，用于训练序列到序列模型.
    data_collator = DataCollatorForSeq2Seq(
        tokenizer=tokenizer,
        pad_to_multiple_of=4 if tokenizer.padding_side == "right" else None,
        # for shift short attention
        label_pad_token_id=dataset_processing.IGNORE_INDEX
        if data_args.ignore_pad_token_for_loss else tokenizer.pad_token_id
    )
    # 重载Seq2SeqTrainer的解码参数
    training_args_dict = training_args.to_dict()
    training_args_dict.update(dict(
        generation_max_length=(
            training_args.generation_max_length or data_args.cutoff_len
        ),
        generation_num_beams=(
            data_args.eval_num_beams or training_args.generation_num_beams
        )
    ))
    training_args = Seq2SeqTrainingArguments(**training_args_dict)
    # 初始化训练器.
    trainer = core.CustomSeq2SeqTrainer(
        model=model,
        args=training_args,
        tokenizer=tokenizer,
        data_collator=data_collator,
        compute_metrics=core.ComputeMetrics(
            tokenizer) if training_args.predict_with_generate else None,
        **dataset_processing.split_dataset(dataset, data_args, training_args)
    )
    # `model.generate`的关键字参数
    gen_kwargs = generating_args.to_dict()
    gen_kwargs["eos_token_id"] = (
            [tokenizer.eos_token_id] + tokenizer.additional_special_tokens_ids
    )
    gen_kwargs["pad_token_id"] = tokenizer.pad_token_id
    gen_kwargs["logits_processor"] = extras.get_logits_processor()
    # 训练
    if training_args.do_train:
        train_result = trainer.train(
            resume_from_checkpoint=training_args.resume_from_checkpoint
        )
        trainer.log_metrics("train", train_result.metrics)
        trainer.save_metrics("train", train_result.metrics)
        trainer.save_state()
        trainer.save_model()
    # 评估
    if training_args.do_eval:
        metrics = trainer.evaluate(metric_key_prefix="eval", **gen_kwargs)
        # 如果启用了predict_with_generate, Eval_loss将出错.
        if training_args.predict_with_generate:
            metrics.pop("eval_loss", None)
        trainer.log_metrics("eval", metrics)
        trainer.save_metrics("eval", metrics)
    # 预测
    if training_args.do_predict:
        predict_results = trainer.predict(
            dataset, metric_key_prefix="predict", **gen_kwargs)
        # 如果启用了predict_with_generate，则Predict_loss将出错.
        if training_args.predict_with_generate:
            predict_results.metrics.pop("predict_loss", None)
        trainer.log_metrics("predict", predict_results.metrics)
        trainer.save_metrics("predict", predict_results.metrics)
        trainer.save_predictions(predict_results)
