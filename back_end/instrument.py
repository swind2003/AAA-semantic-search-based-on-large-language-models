#!/usr/bin/env python3.10.13
"""这是一个辅助功能函数文件
用于帮助其他主要功能的实现

Copyright 2023 Yan Wang.
License(GPL)
Author: Yan Wang
"""
import module


def determine_suffix(file_name: str):
    """
    判断文件的后缀是否是图片文件的后缀
    Args:
        file_name: 文件名字

    Returns:布尔值
    True 表示符合要求
    False 表示不符合要求

    """
    file_list = file_name.split('.')
    suffix = file_list[-1]
    if suffix in {'png', 'jpg', 'JPG', 'PNG'}:
        return True
    return False


def determine_txt_suffix(file_name: str):
    """
    判断文件的后缀是否是图片文件的后缀
    Args:
        file_name: 文件名字

    Returns:布尔值
    True 表示符合要求
    False 表示不符合要求

    """
    file_list = file_name.split('.')
    suffix = file_list[-1]
    if suffix in {'txt'}:
        return True
    return False


def get_time(chat_recorder: module.ChatRecoder):
    """
    获取聊天记录的时间
    Args:
        chat_recorder: 聊天记录对象

    Returns:返回聊天记录的时间

    """
    return chat_recorder.send_time


def get_date(feedback: module.FeedBack):
    """
    获取用户反馈的日期
    Args:
        feedback: 反馈对象

    Returns:返回用户反馈的日期

    """
    return feedback.feedback_date


def get_order_time(order: module.TopUpOrder):
    """
    获取订单的时间
    Args:
        order:订单对象

    Returns:订单的时间

    """
    return order.order_time


def change_to_dict():
    """
    将充值订单类型表中的部分数据转换为字典
    Returns:dict_type字典
    每个键值中包括一个列表{
        订单类型，
        价格
    }
    """
    all_type = module.TopUpType.query.all()
    dict_type = {}
    for order_type in all_type:
        dict_type[f"{order_type.type_id}"] = [order_type.type_name,
                                              order_type.price]
    return dict_type
