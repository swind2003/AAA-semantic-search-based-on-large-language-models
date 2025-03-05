#!/usr/bin/env python3.11.2
"""在训练和推理中构建提示的模板.

Copyright 2023 Zheyun Liu.
License(GPL)
Author: Zheyun Liu.
"""
import tiktoken
from dataclasses import dataclass
from typing import TYPE_CHECKING, Dict, List, Optional, Tuple, Union
if TYPE_CHECKING:
    from transformers import PreTrainedTokenizer


@dataclass
class Template:
    """包含了对话模板的结构和一些用于处理和编码对话的方法.

    Attributes:
        prefix(List[Union[str, Dict[str, str]]]): 用于定义对话的前缀部分.
            可能是字符串列表或包含键值对的字典列表. 这部分内容会在每轮对话开始时被添加到输入中.
        prompt(List[Union[str, Dict[str, str]]]): 用于定义对话提示的部分.
            可能是字符串列表或包含键值对的字典列表. 这部分内容包含了用户输入的内容.
        system(str): 包含有关对话系统信息的字符串，用于描述对话系统或提供对话背景等信息.
        sep(List[Union[str, Dict[str, str]]]): 用于定义分隔符的部分.
            可能是字符串列表或包含键值对的字典列表. 部分内容被用于分隔不同部分的对话内容.
        stop_words(List[str]): 包含需要作为停用词的字符串列表.
            停用词通常是在文本处理中被忽略的常见词语，这些词语对于对话模型的生成可能没有太大意义.
        use_history(bool): 一个布尔值，表示是否使用历史对话记录.
            如果为 True，则模型将使用历史对话记录；否则将忽略历史对话记录.
        efficient_eos(bool): 一个布尔值，表示是否使用高效的结束符.
            如果为 True，则模型将使用一种更有效的方式来标记对话的结束.
    """
    prefix: List[Union[str, Dict[str, str]]]
    prompt: List[Union[str, Dict[str, str]]]
    system: str
    sep: List[Union[str, Dict[str, str]]]
    stop_words: List[str]
    use_history: bool
    efficient_eos: bool

    def encode_oneturn(
            self,
            tokenizer: "PreTrainedTokenizer",
            query: str,
            resp: str,
            history: Optional[List[Tuple[str, str]]] = None,
            system: Optional[str] = None
    ):
        """返回一对分别表示prompt和response的令牌id.

        Args:
            tokenizer(PreTrainedTokenizer): tokenizer.
            query(str): 提问.
            resp(str): 回答.
            history(Optional[List[Tuple[str, str]]]): 历史.
            system(Optional[str): 系统提示词.

        Returns:
            token化的prompt和response元组: Tuple[List[int], List[int]]
        """
        system, history = self._format(query, resp, history, system)
        encoded_pairs = self._encode(tokenizer, system, history)
        prompt_ids = []
        for query_ids, resp_ids in encoded_pairs[:-1]:
            prompt_ids = prompt_ids + query_ids + resp_ids
        prompt_ids, answer_ids = prompt_ids + encoded_pairs[-1][0], \
            encoded_pairs[-1][1]
        return prompt_ids, answer_ids

    def encode_multiturn(
            self,
            tokenizer: "PreTrainedTokenizer",
            query: str,
            resp: str,
            history: Optional[List[Tuple[str, str]]] = None,
            system: Optional[str] = None
    ):
        """返回多对分别表示提示和响应的令牌id.

        Args:
            tokenizer(PreTrainedTokenizer): tokenizer.
            query(str): 提问.
            resp(str): 回答.
            history(Optional[List[Tuple[str, str]]]): 历史.
            system(Optional[str): 系统提示词.

        Returns:
            token化的prompt和response元组列表: List[Tuple[List[int], List[int]]]
        """
        system, history = self._format(query, resp, history, system)
        encoded_pairs = self._encode(tokenizer, system, history)
        return encoded_pairs

    def _format(
            self,
            query: str,
            resp: str,
            history: Optional[List[Tuple[str, str]]] = None,
            system: Optional[str] = None
    ):
        """将输入对齐到标准格式.

        这个函数的主要目的是将输入的查询、回复和历史记录格式化，并根据需要整理成模型可以处理的结构，以便后续对话编码过程的使用.

        Args:
            query(str): 提问.
            resp(str): 回答.
            history(Optional[List[Tuple[str, str]]]): 历史.
            system(Optional[str): 系统提示词.

        Returns:
            返回一个元组，包含经过格式化后的系统信息和格式化后的历史记录:
            Tuple[str, List[Tuple[str, str]]]
        """
        system = system or self.system
        history = history if (history and self.use_history) else []
        history = history + [(query, resp)]
        return system, history

    def _get_special_ids(self, tokenizer: "PreTrainedTokenizer"):
        """用于获取特殊标记的ID.

        这个函数的主要目的是获取起始标记和结束标记的ID列表，用于后续对话编码过程中的特殊标记的处理.

        Args:
            tokenizer(PreTrainedTokenizer): tokenizer.

        Returns:
            返回一个包含两个列表的元组，第一个列表包含起始标记的ID，第二个列表包含结束标记的ID:
            Tuple[List[int], List[int]]
        """
        if tokenizer.bos_token_id is not None and getattr(
                tokenizer, "add_bos_token", True):
            bos_ids = [tokenizer.bos_token_id]
        else:
            bos_ids = []
        if tokenizer.eos_token_id is None:
            raise ValueError("EOS token is required.")
        if self.efficient_eos:
            eos_ids = []
        else:
            eos_ids = [tokenizer.eos_token_id]
        return bos_ids, eos_ids

    def _encode(
            self,
            tokenizer: "PreTrainedTokenizer",
            system: str,
            history: List[Tuple[str, str]]
    ):
        """用于将经过格式化的输入（包括系统信息和历史记录）编码为一对一对的标记ID.

        这个函数的主要目的是将格式化后的对话历史、系统信息等内容转换为模型可以理解的标记ID列表，以便后续模型的输入.
        函数首先调用内部的_get_special_ids方法，获取起始标记和结束标记的ID列表.
        然后使用Tokenizer对格式化的分隔符部分进行编码，得到分隔符的标记ID列表.
        对历史记录中的每一轮对话，根据对话的顺序和格式，使用Tokenizer对格式化后的输入进行编码，得到每一轮对话的查询和回复的标记ID列表.
        最后，将编码后的查询和回复的标记ID列表组成元组，放入一个列表中，并作为函数的返回值返回

        Args:
            tokenizer(PreTrainedTokenizer): tokenizer.
            history(Optional[List[Tuple[str, str]]]): 历史.
            system(Optional[str): 系统提示词.

        Returns:
            返回一个列表，每个元素是一个元组，包含编码后的查询的标记ID列表和编码后的回复的标记ID列表:
            List[Tuple[List[int], List[int]]]
        """
        bos_ids, eos_ids = self._get_special_ids(tokenizer)
        sep_ids = self._convert_inputs_to_ids(tokenizer, context=self.sep)
        encoded_pairs = []
        for turn_idx, (query, resp) in enumerate(history):
            if turn_idx == 0:
                prefix_ids = self._convert_inputs_to_ids(
                    tokenizer, context=self.prefix, system=system)
                if len(prefix_ids) != 0:
                    prefix_ids = bos_ids + prefix_ids + sep_ids
                else:
                    prefix_ids = bos_ids
            else:
                prefix_ids = sep_ids + bos_ids

            query_ids = self._convert_inputs_to_ids(
                tokenizer, context=self.prompt, query=query, idx=str(turn_idx))
            resp_ids = self._convert_inputs_to_ids(tokenizer, context=[resp])
            encoded_pairs.append((prefix_ids + query_ids, resp_ids + eos_ids))
        return encoded_pairs

    @staticmethod
    def _convert_inputs_to_ids(
            tokenizer: "PreTrainedTokenizer",
            context: List[Union[str, Dict[str, str]]],
            system: Optional[str] = None,
            query: Optional[str] = None,
            idx: Optional[str] = None
    ):
        """用于将上下文内容（包括字符串和字典）转换为标记ID的列表.

        这个函数的主要目的是将上下文内容中的字符串和字典中的Token转换为模型可以处理的标记ID列表，以便用于模型的输入.
        函数通过循环遍历上下文内容，对每个元素执行以下操作：
        如果元素是字符串，则使用Tokenizer对字符串进行编码，得到对应的标记ID列表，并将结果追加到最终的标记ID列表中.
        如果元素是字典，且字典中包含键为"token"的项，则将该项的值表示的Token转换为标记ID，然后追加到最终的标记ID列表中.
        最后，返回包含所有上下文内容对应的标记ID列表.

        Args:
            tokenizer(PreTrainedTokenizer): tokenizer.
            context(List[Union[str, Dict[str, str]]]): 上下文内容.
            query(str): 提问.
            system(Optional[str): 系统提示词.
            idx(Optional[str] = None): 可选参数，表示对话轮数的字符串.

        Returns:
            返回一个列表，包含上下文内容对应的标记ID: List[int]
        """
        if isinstance(getattr(tokenizer, "tokenizer", None),
                      tiktoken.Encoding):  # for tiktoken tokenizer (Qwen)
            kwargs = dict(allowed_special="all")
        else:
            kwargs = dict(add_special_tokens=False)
        token_ids = []
        for elem in context:
            if isinstance(elem, str):
                elem = elem.replace("{{system}}", system,
                                    1) if system is not None else elem
                elem = elem.replace("{{query}}", query,
                                    1) if query is not None else elem
                elem = elem.replace("{{idx}}", idx,
                                    1) if idx is not None else elem
                if len(elem) != 0:
                    token_ids = token_ids + tokenizer.encode(elem, **kwargs)
            elif isinstance(elem, dict):
                token_ids = token_ids + [
                    tokenizer.convert_tokens_to_ids(elem.get("token"))]
            else:
                raise ValueError(
                    "Input must be string or dict[str, str], got {}".format(
                        type(elem)))
        return token_ids


# 存放了注册模板的模板字典.
my_template: Template


def register_template(
    prefix: List[Union[str, Dict[str, str]]],
    prompt: List[Union[str, Dict[str, str]]],
    system: str,
    sep: List[Union[str, Dict[str, str]]],
    stop_words: Optional[List[str]] = [],
    use_history: Optional[bool] = True,
    efficient_eos: Optional[bool] = False
):
    """注册函数模板的函数.

    Args:
        prefix(List[Union[str, Dict[str, str]]]): 对话模板的前缀.
        prompt(List[Union[str, Dict[str, str]]]): 对话模板的提示部分.
        system(str): 对话模板的系统信息.
        sep(List[Union[str, Dict[str, str]]]): 对话模板的分隔符部分
        stop_words(Optional[List[str]]): 需要作为停用词的字符串列表.
        use_history(Optional[bool]): 表示是否使用历史对话记录.
        efficient_eos(Optional[bool]): 表示是否使用高效的结束符.
    """
    global my_template
    my_template = Template(
        prefix=prefix,
        prompt=prompt,
        system=system,
        sep=sep,
        stop_words=stop_words,
        use_history=use_history,
        efficient_eos=efficient_eos
    )


"""
注册chatglm3-6b模型的模板.
"""
register_template(
    prefix=[
        {"token": "[gMASK]"},
        {"token": "sop"},
        "{{system}}"
    ],
    prompt=[
        {"token": "<|user|>"},
        "\n",
        "{{query}}",
        {"token": "<|assistant|>"}
    ],
    system="",
    sep=[],
    stop_words=[
        "<|user|>",
        "<|observation|>"
    ],
    efficient_eos=True
)


def get_template_and_fix_tokenizer(tokenizer):
    """这个函数主要用于获取特定名称的对话模板, 并确保与该模板相关联的Tokenizer包含所需的特殊token.

    get_template_and_fix_tokenizer 函数有以下功能：
        检查Tokenizer的特殊token: 函数首先检查传入的Tokenizer是否包含必要的特殊token.
            它会检查eos_token_id和pad_token_id是否存在，如果不存在，则根据需要添加这些token.
        修改Tokenizer的特殊tokens: 在获取模板后，函数会确保Tokenizer包含模板中定义的停用词（stop_words）.
            通过调用 Tokenizer 的 add_special_tokens 方法来添加这些停用词.
        返回模板对象: 最后，函数会返回获取到的模板对象，或者在模板名称未找到时返回None.

    Args:
        tokenizer(PreTrainedTokenizer): 令牌器.
    Returns:
        修改后的Template.
    """
    global my_template
    if tokenizer.eos_token_id is None:
        tokenizer.eos_token = "<|endoftext|>"
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token
    template = my_template
    assert template is not None, "Template does not exist."
    tokenizer.add_special_tokens(
        dict(additional_special_tokens=template.stop_words),
        replace_additional_special_tokens=False
    )
    return template
