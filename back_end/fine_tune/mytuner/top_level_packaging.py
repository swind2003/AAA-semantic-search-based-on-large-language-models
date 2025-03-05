#!/usr/bin/env python3.11.2
"""微调和导出模型的顶层封装.

Copyright 2023 Zheyun Liu.
License(GPL)
Author: Zheyun Liu.
"""
from mytuner import tune
from mytuner.tune import core
from mytuner import chat


def fine_tuning(args=None):
    """对模型继续lora微调.

    Args:
        args (Optional[Dict[str, Any]]): 外部传入的关键字参数.
    """
    model_args, data_args, training_args, finetuning_args, generating_args = (
        tune.get_train_args(args)
    )
    tune.supervise_fine_tuning(
        model_args, data_args, training_args, finetuning_args, generating_args
    )
    print("Fine-tuning finished.")


def export_model(args=None, max_shard_size="10GB"):
    """导出微调后的模型.

    Args:
        args (Optional[Dict[str, Any]]): 外部传入的关键字参数.
        max_shard_size (Optional[str]): 参数的最大分片大小.
    """
    model_args, _, finetuning_args, _ = tune.get_infer_args(args)
    model, tokenizer = (
        core.load_model_and_tokenizer(model_args, finetuning_args, False)
    )
    model.config.use_cache = True
    tokenizer.padding_side = "left"  # restore padding side
    tokenizer.init_kwargs["padding_side"] = "left"
    model.save_pretrained(model_args.export_dir, max_shard_size=max_shard_size)
    try:
        tokenizer.save_pretrained(model_args.export_dir)
    except Exception:
        print("无法保存分词器，请手动复制文件.")
    print("The function named export_model have not been implemented yet.")


def stream_chat(args=None):
    """流式对话.

        Args:
            args (Optional[Dict[str, Any]]): 外部传入的关键字参数.
    """
    # 对话模型
    chat_model = chat.ChatModel(args)
    # 对话历史
    history = []
    print("输入exit退出，输入clear清空对话历史.输入history打印历史对话")
    while True:
        # 获取输入
        try:
            query = input("\nUser: ")
        except UnicodeDecodeError:
            print(
                "Detected decoding error at the inputs, "
                "please set the terminal encoding to utf-8.")
            continue
        except Exception:
            raise
        # 判断对话
        if query.strip() == "exit":
            break
        # 判断历史
        if query.strip() == "clear":
            history = []
            print("History has been removed.")
            continue
        if query.strip() == "history":
            print("History:")
            for chat_list in history:
                user, ai = chat_list
                print(f"User said: {user}\nAI said: {ai}")
            print("That's all the conversation history.")
            continue
        print("Assistant: ", end="", flush=True)
        response = ""
        for new_text in chat_model.stream_chat(query, history):
            print(new_text, end="", flush=True)
            response += new_text
        print()
        history = history + [(query, response)]
