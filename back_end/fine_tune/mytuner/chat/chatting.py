#!/usr/bin/env python3.11.2
"""模型对话相关.

Copyright 2023 Zheyun Liu.
License(GPL)
Author: Zheyun Liu.
"""
import torch
from typing import Any, Dict, Generator, List, Optional, Tuple
from threading import Thread
from transformers import GenerationConfig, TextIteratorStreamer
from mytuner import extras
from mytuner import tune
from mytuner.tune import core


class ChatModel:
    """实现了一个聊天模型.

    Attributes:
        generating_args (GeneratingArguments): 解码参数类.
        model (PreTrainedModel): 模型.
        tokenizer (PreTrainedTokenizer): 分词器.
        template (Template): 对话模板.
        system_prompt (Optional[str]): 系统提示词.
    """
    def __init__(self, args: Optional[Dict[str, Any]] = None):
        model_args, data_args, finetuning_args, self.generating_args = (
            tune.get_infer_args(args))
        self.model, self.tokenizer = core.load_model_and_tokenizer(
            model_args, finetuning_args)
        self.tokenizer.padding_side = "left"
        self.model = extras.dispatch_model(self.model)
        self.template = extras.get_template_and_fix_tokenizer(self.tokenizer)
        self.system_prompt = data_args.system_prompt

    def process_args(
        self,
        query: str,
        history: Optional[List[Tuple[str, str]]] = None,
        system: Optional[str] = None,
        **input_kwargs
    ):
        """处理聊天模型的输入, 将用户提供的查询信息转换为模型生成回复所需的参数.

        Args:
            query (str): 用户提供的查询信息.
            history (Optional[List[Tuple[str, str]]]): 记录对话历史.
            system (Optional[str]): 系统提示语.
            input_kwargs: 其他可能的输入参数.

        Returns:
            Tuple[Dict[str, Any], int]
        """
        # 根据传递进来的查询信息、历史对话和系统提示，使用模板编码生成提示序列.
        system = system or self.system_prompt
        prompt, _ = self.template.encode_oneturn(
            tokenizer=self.tokenizer,
            query=query,
            resp="",
            history=history,
            system=system
        )
        prompt_length = len(prompt)
        # 这个提示序列将用作模型的输入.
        input_ids = torch.tensor([prompt], device=self.model.device)
        # 计算生成的提示序列的长度，以便后续使用.
        # 提示序列的长度将在生成回复时用于确定模型生成的回复开始的位置.
        do_sample = input_kwargs.pop("do_sample", None)
        temperature = input_kwargs.pop("temperature", None)
        top_p = input_kwargs.pop("top_p", None)
        top_k = input_kwargs.pop("top_k", None)
        num_return_sequences = input_kwargs.pop("num_return_sequences", None)
        repetition_penalty = input_kwargs.pop("repetition_penalty", None)
        max_length = input_kwargs.pop("max_length", None)
        max_new_tokens = input_kwargs.pop("max_new_tokens", None)
        # 根据传递的参数和默认的生成参数，组装生成回复所需的参数字典
        # 更新生成参数字典中的值，这些值可能会根据用户提供的参数而改变，如采样方式、温度、top-k、top-p等.
        generating_args = self.generating_args.to_dict()
        generating_args.update(dict(
            do_sample=(do_sample
                       if do_sample is not None
                       else generating_args["do_sample"]),
            temperature=temperature or generating_args["temperature"],
            top_p=top_p or generating_args["top_p"],
            top_k=top_k or generating_args["top_k"],
            # 要生成的回答数量--------------------------------
            num_return_sequences=num_return_sequences or 1,
            # ---------------------------------------------
            repetition_penalty=(repetition_penalty
                                or generating_args["repetition_penalty"]),
            eos_token_id=([self.tokenizer.eos_token_id]
                          + self.tokenizer.additional_special_tokens_ids),
            pad_token_id=self.tokenizer.pad_token_id
        ))
        # 如果需要生成多个回复，会相应地调整生成参数
        if isinstance(num_return_sequences, int) and num_return_sequences > 1:
            generating_args["do_sample"] = True
        if max_length:
            generating_args.pop("max_new_tokens", None)
            generating_args["max_length"] = max_length
        if max_new_tokens:
            generating_args.pop("max_length", None)
            generating_args["max_new_tokens"] = max_new_tokens
        gen_kwargs = dict(
            inputs=input_ids,
            generation_config=GenerationConfig(**generating_args),
            logits_processor=extras.get_logits_processor()
        )
        return gen_kwargs, prompt_length

    @torch.inference_mode()
    def chat(
        self,
        query: str,
        history: Optional[List[Tuple[str, str]]] = None,
        system: Optional[str] = None,
        **input_kwargs
    ):
        """根据给定的输入参数生成聊天回复.

        一次性调用模型的 generate 方法生成完整的聊天回复文本.
        同步执行，直接获取完整的回复文本并返回.
        适合于小规模的、对实时性要求不高的场景.

        Args:
            query (str): 用户提供的查询信息.
            history (Optional[List[Tuple[str, str]]]): 对话历史.
            system (Optional[str]): 系统提示语.
            input_kwargs: 其他可能的输入参数.

        Returns:
            Tuple[List[str], Tuple[int, int]]
            返回一个元组，包含生成的聊天回复的字符串列表和一个元组.
            字符串列表包含模型生成的回复文本.
            元组包含两个整数，分别表示输入的提示序列长度和生成的回复长度.
        """
        # 使用 process_args 方法根据传递进来的参数，获取生成回复所需的参数和提示序列的长度.
        gen_kwargs, prompt_length = self.process_args(
            query,
            history,
            system,
            **input_kwargs
        )
        # 使用模型的 generate 方法根据提供的参数生成聊天回复.
        generate_output = self.model.generate(**gen_kwargs)
        # 将生成的回复从模型输出中提取出来
        response_ids = generate_output[:, prompt_length:]
        response = self.tokenizer.batch_decode(
            response_ids,
            skip_special_tokens=True,
            clean_up_tokenization_spaces=True
        )
        # 计算生成的回复的长度，去除了特殊标记（如结束标记），以便后续使用.
        response_length = 0
        for i in range(len(response_ids)):
            eos_index = (
                response_ids[i] == self.tokenizer.eos_token_id
            ).nonzero()
            response_length += eos_index[0].item() \
                if len(eos_index) else len(response_ids[i])
        return response, (prompt_length, response_length)

    @torch.inference_mode()
    def stream_chat(
        self,
        query: str,
        history: Optional[List[Tuple[str, str]]] = None,
        system: Optional[str] = None,
        **input_kwargs
    ):
        """以流式方式生成聊天回复.

        以生成器的形式实现，采用流式处理的方式逐步生成模型的聊天回复文本.
        使用了异步处理，在一个单独的线程中调用模型的 generate 方法，逐步将生成的文本发送到流式处理器中.
        更适合处理大量请求或需要即时响应的情况.

        Args:
            query (str): 用户提供的查询信息.
            history (Optional[List[Tuple[str, str]]]): 对话历史.
            system (Optional[str]): 系统提示语.
            input_kwargs: 其他可能的输入参数.

        Returns:
            Generator[str, None, None]
            返回的生成器对象会输出生成的聊天回复文本.
            采用异步处理方式以提高处理大量请求时的性能和响应速度.
        """
        # 使用 process_args 方法根据传递进来的参数，获取生成回复所需的参数.
        gen_kwargs, _ = self.process_args(query, history, system, **input_kwargs)
        # 创建一个 TextIteratorStreamer 对象用于流式处理生成的文本.
        # 为了进行异步处理，设置了超时时间等参数.
        streamer = TextIteratorStreamer(
            self.tokenizer,
            timeout=60.0,
            skip_prompt=True,
            skip_special_tokens=True
        )
        gen_kwargs["streamer"] = streamer
        # 通过创建一个新的线程，在该线程中调用模型的 generate 方法以异步方式生成聊天回复.
        # 将生成的文本流式地送入 TextIteratorStreamer 对象中.
        thread = Thread(target=self.model.generate, kwargs=gen_kwargs)
        thread.start()
        yield from streamer
