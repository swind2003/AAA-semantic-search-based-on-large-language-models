#!/usr/bin/env python3.10.13
"""这是一个ORM模型文件

Copyright 2023 Yan Wang.
License(GPL)
Author: Yan Wang
"""
import flask_login
from sqlalchemy.sql import functions
from sqlalchemy import sql
import extentions


# TODO 表与表之间可以采用relationship，减少查表
class HeadPortrait(extentions.DATABASE.Model):
    """
    头像表
    公共属性为：
    head_portrait_id 头像编号
    path 路径
    """
    __tablename__ = "head_portrait"
    head_portrait_id = extentions.DATABASE.Column(extentions.DATABASE.Integer,
                                                  primary_key=True,
                                                  autoincrement=True)
    path = extentions.DATABASE.Column(extentions.DATABASE.String(100),
                                      nullable=False)


class UserType(extentions.DATABASE.Model):
    """
    用户类型表
    公共属性为：
    user_type_id 用户类型编号 0 1 2 3
    type_name 类型名称
    """
    __tablename__ = "user_type"
    user_type_id = extentions.DATABASE.Column(extentions.DATABASE.Integer,
                                              primary_key=True,
                                              autoincrement=True)
    type_name = extentions.DATABASE.Column(extentions.DATABASE.String(20),
                                           nullable=False,
                                           unique=True)


class User(flask_login.UserMixin, extentions.DATABASE.Model):
    """
    用户表
    user_id 用户编号
    user_type_id 用户类型编号
    head_portrait_id  头像编号
    mail_account 邮箱
    password 密码
    nickname 昵称
    sex 性别 男 女
    restriction_time 限制登录时间 默认为0 单位是天
    vip_time_raiming    VIP剩余时间 默认为0 单位是天
    query_times 每小时询问次数 普通用户默认为8，vip用户为30次
    limit 是否被限制询问次数
    current_query_times 当前可提问次数
    advertise_state 广告的显示与否
    """
    __tablename__ = "users"
    user_id = extentions.DATABASE.Column(extentions.DATABASE.Integer,
                                         primary_key=True, autoincrement=True)
    user_type_id = extentions.DATABASE.Column(
        extentions.DATABASE.Integer,
        extentions.DATABASE.ForeignKey("user_type.user_type_id"),
        server_default=sql.text('3'))
    head_portrait_id = extentions.DATABASE.Column(
        extentions.DATABASE.Integer,
        extentions.DATABASE.ForeignKey("head_portrait.head_portrait_id"),
        server_default=sql.text('1'))
    mail_account = extentions.DATABASE.Column(extentions.DATABASE.String(50),
                                              nullable=False,
                                              unique=True)
    password = extentions.DATABASE.Column(extentions.DATABASE.String(12),
                                          nullable=False)
    nickname = extentions.DATABASE.Column(
        extentions.DATABASE.String(20),
        nullable=False,
        server_default=sql.text('"用户"'))
    sex = extentions.DATABASE.Column(extentions.DATABASE.Enum('男', '女'),
                                     nullable=True)
    restriction_time = extentions.DATABASE.Column(
        extentions.DATABASE.Integer,
        server_default=sql.text('0'),
        nullable=False)
    vip_time_raiming = extentions.DATABASE.Column(extentions.DATABASE.Integer,
                                                  server_default=sql.text('0'),
                                                  nullable=False)
    query_times = extentions.DATABASE.Column(extentions.DATABASE.Integer,
                                             server_default=sql.text('8'),
                                             nullable=False)
    limit = extentions.DATABASE.Column(extentions.DATABASE.Boolean,
                                       server_default=sql.text("FALSE"))
    current_query_times = extentions.DATABASE.Column(
        extentions.DATABASE.Integer,
        server_default=sql.text('8'),
        nullable=False)
    advertise_state = extentions.DATABASE.Column(
        extentions.DATABASE.Boolean,
        server_default=sql.text("FALSE"))

    def get_id(self):
        """
        获取模型表的标识
        Returns:
        user_id
        """
        return str(self.user_id)


class FeedBack(extentions.DATABASE.Model):
    """
    反馈表
    feedback_id 编号
    user_id 用户编号
    feedback_date 提交反馈的日期
    content 内容
    is_checked 是否查看 0表示未查看 1表示已查看
    """
    __tablename__ = "feedback"
    feedback_id = extentions.DATABASE.Column(extentions.DATABASE.Integer,
                                             primary_key=True,
                                             autoincrement=True)
    user_id = extentions.DATABASE.Column(
        extentions.DATABASE.Integer,
        extentions.DATABASE.ForeignKey("users.user_id",
                                       ondelete='CASCADE'))
    feedback_date = extentions.DATABASE.Column(
        extentions.DATABASE.Date,
        nullable=False
    )
    content = extentions.DATABASE.Column(extentions.DATABASE.Text,
                                         nullable=False)
    is_checked = extentions.DATABASE.Column(extentions.DATABASE.Boolean,
                                            server_default=sql.text('false'))


class ChatWindowGroup(extentions.DATABASE.Model):
    """
    聊天窗口分组表
    group_id  分组编号
    user_id 用户编号
    group_name 分组名称
    """
    __tablename__ = "chat_window_group"
    group_id = extentions.DATABASE.Column(extentions.DATABASE.Integer,
                                          primary_key=True,
                                          autoincrement=True)
    user_id = extentions.DATABASE.Column(
        extentions.DATABASE.Integer,
        extentions.DATABASE.ForeignKey("users.user_id", ondelete='CASCADE'))
    group_name = extentions.DATABASE.Column(extentions.DATABASE.String(100),
                                            server_default=sql.text('"分组"'))


class ChatWindow(extentions.DATABASE.Model):
    """
    聊天窗口表
    chat_window_id 窗口编号
    user_id 用户编号
    group_id 分组编号
    chat_window_name 窗口名字
    """
    __tablename__ = "chat_window"
    chat_window_id = extentions.DATABASE.Column(extentions.DATABASE.Integer,
                                                primary_key=True,
                                                autoincrement=True)
    user_id = extentions.DATABASE.Column(
        extentions.DATABASE.Integer,
        extentions.DATABASE.ForeignKey("users.user_id"))
    group_id = extentions.DATABASE.Column(
        extentions.DATABASE.Integer,
        extentions.DATABASE.ForeignKey("chat_window_group.group_id",
                                       ondelete='CASCADE'))
    chat_window_name = extentions.DATABASE.Column(
        extentions.DATABASE.String(100),
        server_default=sql.text('"窗口"'))


class ChatRecoder(extentions.DATABASE.Model):
    """
    聊天记录表
    chat_recoder_id 记录编号
    chat_window_id 窗口编号
    send_time 发送时间
    content 内容
    """
    __tablename__ = "chat_recoder"
    chat_recoder_id = extentions.DATABASE.Column(
        extentions.DATABASE.Integer,
        primary_key=True,
        autoincrement=True)
    chat_window_id = extentions.DATABASE.Column(
        extentions.DATABASE.Integer,
        extentions.DATABASE.ForeignKey("chat_window.chat_window_id",
                                       ondelete='CASCADE'))
    send_time = extentions.DATABASE.Column(extentions.DATABASE.DateTime,
                                           server_default=functions.func.now())
    content = extentions.DATABASE.Column(extentions.DATABASE.Text,
                                         nullable=False)


class ErrorType(extentions.DATABASE.Model):
    """
    错误类型表
    error_id 错误编号
    error_code 错误码
    error_name 错误名称
    error_description 错误描述
    """
    __tablename__ = "error_type"
    error_id = extentions.DATABASE.Column(extentions.DATABASE.Integer,
                                          primary_key=True,
                                          autoincrement=True)
    error_code = extentions.DATABASE.Column(extentions.DATABASE.String(4),
                                            nullable=False,
                                            unique=True)
    error_name = extentions.DATABASE.Column(extentions.DATABASE.String(50),
                                            nullable=False,
                                            unique=True)
    error_description = extentions.DATABASE.Column(extentions.DATABASE.Text,
                                                   nullable=False)


class ErrorLog(extentions.DATABASE.Model):
    """
    错误日志
    error_log_id 日志编号
    error_id 错误编号
    error_time 发生错误时间
    """
    __tablename__ = "error_log"
    error_log_id = extentions.DATABASE.Column(extentions.DATABASE.Integer,
                                              primary_key=True,
                                              autoincrement=True)
    # user_id = extentions.DATABASE.Column(
    #     extentions.DATABASE.Integer,
    #     extentions.DATABASE.ForeignKey("users.user_id", ondelete='CASCADE'))
    error_id = extentions.DATABASE.Column(
        extentions.DATABASE.Integer,
        extentions.DATABASE.ForeignKey("error_type.error_id"))
    error_time = extentions.DATABASE.Column(
        extentions.DATABASE.DateTime,
        server_default=functions.func.now())


class LoginLog(extentions.DATABASE.Model):
    """
    登录日志表
    login_id 登录日志编号
    user_id 用户编号
    log_time 登录时间
    """
    __tablename__ = "login_log"
    login_id = extentions.DATABASE.Column(extentions.DATABASE.Integer,
                                          primary_key=True,
                                          autoincrement=True)
    user_id = extentions.DATABASE.Column(
        extentions.DATABASE.Integer,
        extentions.DATABASE.ForeignKey("users.user_id", ondelete='CASCADE'))
    log_time = extentions.DATABASE.Column(
        extentions.DATABASE.DateTime,
        server_default=functions.func.now())


class LogoutLog(extentions.DATABASE.Model):
    """
    登出日志表
    logout_id 登出日志编号
    user_id 用户编号
    log_time登出时间
    """
    __tablename__ = "logout_log"
    logout_id = extentions.DATABASE.Column(extentions.DATABASE.Integer,
                                           primary_key=True,
                                           autoincrement=True)
    user_id = extentions.DATABASE.Column(
        extentions.DATABASE.Integer,
        extentions.DATABASE.ForeignKey("users.user_id", ondelete='CASCADE'))
    logout_time = extentions.DATABASE.Column(
        extentions.DATABASE.DateTime,
        server_default=functions.func.now())


class UserRole(extentions.DATABASE.Model):
    """
    用户自定义角色表
    role_id  角色编号
    user_id 用户编号
    role_name 角色名字
    head_portrait_id 角色头像编号
    description 角色描述
    divergency 发散程度
    module_name 模型名字
    data_path 文档存放路径
    prompt 提示词
    is_collect: 是否被收藏
    """
    __tablename__ = "user_desgin_role"
    role_id = extentions.DATABASE.Column(extentions.DATABASE.Integer,
                                         primary_key=True,
                                         autoincrement=True)
    user_id = extentions.DATABASE.Column(
        extentions.DATABASE.Integer,
        extentions.DATABASE.ForeignKey("users.user_id", ondelete='CASCADE'))
    role_name = extentions.DATABASE.Column(extentions.DATABASE.String(50),
                                           unique=False,
                                           nullable=False)
    head_portrait_id = extentions.DATABASE.Column(
        extentions.DATABASE.Integer,
        extentions.DATABASE.ForeignKey("head_portrait.head_portrait_id"),
        server_default=sql.text('Null'))
    description = extentions.DATABASE.Column(extentions.DATABASE.Text,
                                             nullable=False)
    divergency = extentions.DATABASE.Column(extentions.DATABASE.Integer,
                                            nullable=False)
    module_name = extentions.DATABASE.Column(extentions.DATABASE.String(20),
                                             nullable=False)
    module_api = extentions.DATABASE.Column(extentions.DATABASE.String(100),
                                            nullable=False)
    prompt = extentions.DATABASE.Column(extentions.DATABASE.Text,
                                        nullable=False)
    is_collect = extentions.DATABASE.Column(extentions.DATABASE.Boolean,
                                            server_default=sql.text('false'))


class BuiltInRole(extentions.DATABASE.Model):
    """
    内置角色表
    role_id 角色编号
    role_name 角色名称
    head_portrait_id 角色头像编号
    description 描述
    divergency 发散程度
    module_name 模型名字
    module_api 模型api
    prompt 提示词
    """
    __tablename__ = "built_in_role"
    role_id = extentions.DATABASE.Column(extentions.DATABASE.Integer,
                                         primary_key=True,
                                         autoincrement=True)
    role_name = extentions.DATABASE.Column(extentions.DATABASE.String(50),
                                           unique=True)
    head_portrait_id = extentions.DATABASE.Column(
        extentions.DATABASE.Integer,
        extentions.DATABASE.ForeignKey("head_portrait.head_portrait_id"),
        server_default=sql.text('Null'))
    description = extentions.DATABASE.Column(extentions.DATABASE.Text,
                                             nullable=False)
    divergency = extentions.DATABASE.Column(extentions.DATABASE.Integer,
                                            nullable=False)
    module_name = extentions.DATABASE.Column(extentions.DATABASE.String(20),
                                             nullable=False)
    module_api = extentions.DATABASE.Column(extentions.DATABASE.String(100),
                                            nullable=False)
    prompt = extentions.DATABASE.Column(extentions.DATABASE.Text,
                                        nullable=False)
    have_document_store = extentions.DATABASE.Column(
        extentions.DATABASE.Boolean,
        nullable=False,
        server_default=sql.text('TRUE')
    )


# class BuiltInRoleData(extentions.DATABASE.Model):
#     """
#     内置角色的文档表
#     data_id 文档数据编号
#     Role_id 角色编号
#     data_path 文档路径
#     """
#     __tablename__ = "built_in_role_data"
#     data_id = extentions.DATABASE.Column(extentions.DATABASE.Integer,
#                                          primary_key=True,
#                                          autoincrement=True)
#     Role_id = extentions.DATABASE.Column(
#         extentions.DATABASE.Integer,
#         extentions.DATABASE.ForeignKey("built_in_role.role_id"))
#     data_path = extentions.DATABASE.Column(extentions.DATABASE.String(100),
#                                            nullable=False,
#                                            unique=True)


class TopUpType(extentions.DATABASE.Model):
    """
    订单类型表
    type_id 订单类型编号
    typename 会员类型名称
    valid_time 优先时长
    price 价格
    """
    __tablename__ = "top_up_type"
    type_id = extentions.DATABASE.Column(extentions.DATABASE.Integer,
                                         primary_key=True,
                                         autoincrement=True)
    type_name = extentions.DATABASE.Column(extentions.DATABASE.String(4),
                                           nullable=False)
    valid_time = extentions.DATABASE.Column(extentions.DATABASE.Integer,
                                            nullable=False)
    price = extentions.DATABASE.Column(extentions.DATABASE.Integer,
                                       nullable=False)


class TopUpOrder(extentions.DATABASE.Model):
    """
    充值订单表
    order_id 订单编号
    user_id 用户编号
    type_id 类型编号
    order_time 订单时间
    """
    __tablename__ = "top_up_order"
    order_id = extentions.DATABASE.Column(extentions.DATABASE.Integer,
                                          primary_key=True,
                                          autoincrement=True)
    user_id = extentions.DATABASE.Column(
        extentions.DATABASE.Integer,
        extentions.DATABASE.ForeignKey("users.user_id", ondelete='CASCADE'))
    type_id = extentions.DATABASE.Column(
        extentions.DATABASE.Integer,
        extentions.DATABASE.ForeignKey("top_up_type.type_id"))
    order_time = extentions.DATABASE.Column(extentions.DATABASE.DateTime,
                                            server_default=functions.func.now())
