#!/usr/bin/env python3.11.2
"""模型微调和导出的参数.

Copyright 2023 Zheyun Liu.
License(GPL)
Author: Zheyun Liu.
"""
# 在Linux系统允许的时候记得把所有路径里的双反斜杠改为单斜杆.
fine_tuning_args = {
    # 源模型的路径
    "model_name_or_path": "data_file\\models\\chatglm3-6b",
    # 是否是训练阶段
    "do_train": True,
    # 使用的数据集所在的文件夹
    "dataset_dir": "data_file\\data",
    # 使用的数据集名称
    "dataset": "my_law_train_small",
    # 分词后模型输入的最大长度
    "cutoff_len": 1024,
    # 学习率
    "learning_rate": 0.0001,
    # 训练几轮数据
    "num_train_epochs": 3.0,
    # 截断数据集的训练样例数量
    "max_samples": 160000,
    # 每个设备的批容量
    "per_device_train_batch_size": 4,
    # 梯度累积步长, 即每几次梯度下降求值保存
    "gradient_accumulation_steps": 4,
    # 要使用的调度器类型
    "lr_scheduler_type": "cosine",
    # 最大梯度范数(用于梯度裁剪).
    "max_grad_norm": 1.0,
    # 两个日志之间的更新步骤数, 应该是[0,1)范围内的整数或浮点数. 如果小于1, 则解释为总训练步数的比例.
    "logging_steps": 5,
    # 两个检查点保存之前的更新步骤数, 应该是[0,1)范围内的整数或浮点数. 如果小于1, 则解释为总训练步数的比例.
    "save_steps": 100,
    # 线性热身从0到learning_rate的步数, 默认是0
    "warmup_steps": 0,
    # 是否在提示符中禁用掩码
    "train_on_prompt": False,
    # 是否向上转型fp32中的layernorm权重.
    "upcast_layernorm": False,
    # loRA微调的内在维度
    "lora_rank": 8,
    # loRA微调的丢弃率
    "lora_dropout": 0.1,
    # 要进行loRA微调的目标模块名称
    "lora_target": "query_key_value",
    # 是从最后一个LoRA权重恢复训练还是在合并它们后创建新的权重
    "resume_lora_training": True,
    # 导出位置
    "output_dir": "data_file\\saves\\my_model_01",
    # 计算使用的数据类型
    "bf16": True,
}


export_model_args = {
    # 源模型路径
    "model_name_or_path": "data_file\\models\\chatglm3-6b",
    # 检查点路径
    "checkpoint_dir": "data_file\\saves\\my_model_01",
    # 导出位置
    "export_dir": "data_file\\trained_model"
}


chat_args = {
    # 源模型路径
    "model_name_or_path": "data_file\\glm-law",
    # 检查点路径
    # "checkpoint_dir": "data_file\\saves\\my_model_01"
}
