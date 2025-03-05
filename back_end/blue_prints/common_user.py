#!/usr/bin/env python3.10.13
"""这是一个对前端页面提供用户使用的API接口文件

Copyright 2023 Yan Wang.
License(GPL)
Author: Yan Wang
"""
import datetime
import os
import flask
import flask_login
from flask import blueprints
import qrcode
import extentions
import module
import instrument


USER_BLUE_PRINT = blueprints.Blueprint("user", __name__,
                                       url_prefix="/user")


@USER_BLUE_PRINT.route("/information/set", methods=['POST'])
@flask_login.login_required
def change_information():
    """该视图用于修改个人信息

    Returns:json格式数据
    code 200 表示成功
         400 表示失败

    """
    form = flask.request.get_json()
    if CommenUser.set_information(**form):
        code = "200"
    else:
        code = "400"
    return flask.jsonify({"code": code})


@USER_BLUE_PRINT.route("/information/change", methods=['POST'])
@flask_login.login_required
def change_password():
    """修改密码
    获取前端的请求参数，然后进行密码的修改

    Returns:json格式数据
    code 200 表示成功
         400 表示失败
         401 表示原密码输入错误

    """
    form = flask.request.get_json()
    user_id = form.get("user_id")
    old_password = form.get("old_password")
    new_password = form.get("new_password")
    code = CommenUser.change_password(user_id, new_password, old_password)
    return flask.jsonify(code=code)


@USER_BLUE_PRINT.route("/chat/get_all_group", methods=['GET'])
@flask_login.login_required
def get_all_group():
    """获取所有分组信息的视图

    根据用户id，查询所有该用户的分组信息
    Returns:json数据
    包含多个对象，其中每个对象都包含group_id和group_name

    """
    user_id = flask.request.args.get("user_id")
    response = []
    if user_id:
        response = CommenUser.search_all_group(user_id)
    return flask.jsonify(data=response)


@USER_BLUE_PRINT.route("/chat/get_all_window", methods=['GET'])
@flask_login.login_required
def get_all_window():
    """
    获取所有聊天窗口的视图
    Returns:
    获取成功则返回所有聊天窗口的信息
    失败则返回空的信息
    """
    user_id = flask.request.args.get("user_id")
    response = CommenUser.search_all_window(user_id)
    return flask.jsonify(data=response)


@USER_BLUE_PRINT.route("/chat/get_all_role", methods=['GET'])
@flask_login.login_required
def get_all_role():
    """
    获取所有角色信息，并返回给前端
    Returns:json数据
    其中包含多个对象
    每个对象都包含role_id, role_name, llm_type

    """
    user_id = flask.request.args.get("user_id")
    response = []
    if user_id:
        user = module.User.query.get(user_id)
        if user:
            if user.vip_time_raiming != 0:
                user_role_list = (module.UserRole.query.
                                  filter_by(user_id=user_id).all())
                if len(user_role_list) != 0:
                    user_role_list.sort(
                        key=lambda user_role: user_role.is_collect,
                        reverse=True)
                for role in user_role_list:
                    json_data = {
                        "flag": f"{role.role_id}_1",
                        "role_id": role.role_id,
                        "role_name": role.role_name,
                        "llm_type": "1"
                    }
                    response.append(json_data)
        role_list = module.BuiltInRole.query.all()
        for role in role_list:
            json_data = {
                "flag": f"{role.role_id}_0",
                "role_id": role.role_id,
                "role_name": role.role_name,
                "llm_type": "0"
            }
            response.append(json_data)
    return flask.jsonify(data=response)


@USER_BLUE_PRINT.route("/chat/new_chat", methods=['POST'])
@flask_login.login_required
def new_chat_window():
    """
    新建聊天窗口的视图函数
    Returns:json数据
    code 200表示成功 400表示失败
    chat_window_id 聊天窗口id

    """
    form = flask.request.get_json()
    user_id = form.get("user_id")
    group_id = form.get("group_id")
    code = "401"
    if user_id == "" or group_id == "":
        return flask.jsonify({"code": code, "message": "参数有误！"})
    success, chat_window_id = CommenUser.add_chat_window(user_id=user_id,
                                                         group_id=group_id)
    if success:
        code = "200"
    else:
        code = "400"
    return flask.jsonify({"code": code, "chat_window_id": chat_window_id})


@USER_BLUE_PRINT.route("/chat/rename_window", methods=['POST'])
@flask_login.login_required
def rename_window():
    """
    重命名窗口函数

    Returns:json数据
    code 200表示成功
         400表示失败

    """
    form = flask.request.get_json()
    chat_window_id = form.get('chat_window_id')
    chat_window_name = form.get('chat_window_name')
    success = CommenUser.rename_chat_window(chat_window_id, chat_window_name)
    if success:
        code = "200"
    else:
        code = "400"
    return flask.jsonify({"code": code})


@USER_BLUE_PRINT.route("/chat/delete_window", methods=['DELETE'])
@flask_login.login_required
def delete_window():
    """
    删除聊天窗口视图
    Returns:json数据
    code 200表示成功
         400表示失败
    """
    chat_window_id = flask.request.args.get("chat_window_id", "")
    if chat_window_id != "":
        chat_window_id = chat_window_id
        success = CommenUser.delete_chat_window(chat_window_id)
        if success:
            code = "200"
        else:
            code = "400"
        return flask.jsonify({"code": code})
    return flask.jsonify({"code": "400"})


@USER_BLUE_PRINT.route("/chat/new_group", methods=['POST'])
@flask_login.login_required
def new_group():
    """
    新建分组视图
    Returns:json数据
    code 200表示成功
         400表示失败
    group_id 表示分组的编号
    """
    form = flask.request.get_json()
    user_id = form.get("user_id")
    group_name = form.get("group_name")
    success, group_id = CommenUser.add_window_group(user_id=user_id,
                                                    group_name=group_name)
    if success:
        code = "200"
    else:
        code = "400"
    return flask.jsonify({"code": code, "group_id": group_id})


@USER_BLUE_PRINT.route("/chat/rename_group", methods=['POST'])
@flask_login.login_required
def rename_group():
    """
    重命名分组
    Returns:json数据
    code 200表示成功
         400表示失败

    """
    form = flask.request.get_json()
    group_id = form.get("group_id")
    group_name = form.get("group_name")
    success = CommenUser.rename_window_group(group_name, group_id)
    if success:
        code = "200"
    else:
        code = "400"
    return flask.jsonify({"code": code})


@USER_BLUE_PRINT.route("/chat/delete_group", methods=['DELETE'])
@flask_login.login_required
def delete_group():
    """
    删除分组函数
    Returns:json数据
    code 200表示成功
         400表示失败

    """
    group_id = flask.request.args.get("group_id")
    success = CommenUser.delete_window_group(group_id)
    if success:
        code = "200"
    else:
        code = "400"
    return flask.jsonify({"code": code})


@USER_BLUE_PRINT.route("/chat/group_add_window", methods=['POST'])
@flask_login.login_required
def group_add_window():
    """
    往分组当中添加聊天窗口
    Returns:json数据
    code 200表示成功
         400表示失败

    """
    form = flask.request.get_json()
    chat_window_id = form.get("chat_window_id")
    group_id = form.get("group_id")
    chat_window = module.ChatWindow.query.get(chat_window_id)
    if chat_window:
        chat_window.group_id = group_id
        extentions.DATABASE.session.commit()
        code = "200"
    else:
        code = "400"
    return flask.jsonify({"code": code})


@USER_BLUE_PRINT.route("/information/get", methods=['GET'])
@flask_login.login_required
def get_information():
    """
    获取用户信息视图
    Returns:json数据
    其中包含用户的多个信息
    其中code 200表示获取成功
            400表示获取失败

    """
    user_id = int(flask.request.args.get("user_id", "0"))
    if user_id != 0:
        dict_information = CommenUser.get_information(user_id)
        return flask.jsonify(**dict_information)
    return flask.jsonify(code="400")


@USER_BLUE_PRINT.route("/information/get_head_portrait", methods=['GET'])
def get_head_portrait():
    user_id = flask.request.args.get('user_id')
    user = module.User.query.get(user_id)
    if user:
        head_portrait = module.HeadPortrait.query.get(user.head_portrait_id)
        if head_portrait:
            path = head_portrait.path
            return flask.send_file(path)
    return flask.jsonify(code="400", message="获取头像出错")


@USER_BLUE_PRINT.route("/information/change_headportrait", methods=['POST'])
@flask_login.login_required
def change_head_portrait():
    """
    修改头像视图
    Returns:json数据
    code 200表示成功
         400表示失败
    message描述

    """
    file = flask.request.files.get('file')
    code = "400"
    if file:
        file_name = file.filename
        user_id = flask.request.form.get('user_id')
        if instrument.determine_suffix(file_name):
            path = f"aaa_file/headportrait/{user_id + file_name}"
            success = CommenUser.change_head_portrait(user_id, path)
            file.save(dst=path)
            if success:
                code = "200"
            else:
                return flask.jsonify({"code": code, "message": "头像修改失败"})
            return flask.jsonify(
                {"code": code, "message": "头像修改成功"})
        return flask.jsonify({"code": code, "message": "图片格式不符合要求"})
    return flask.jsonify({"code": code, "message": "头像修改失败"})


@USER_BLUE_PRINT.route("/chat/get_recorder", methods=['GET'])
@flask_login.login_required
def get_recorder():
    """
    获取聊天记录视图
    Returns:json数据
    包含多条聊天记录
    """
    chat_window_id = flask.request.args.get("chat_window_id")
    all_chat_recorder = (module.ChatRecoder.query.
                         filter_by(chat_window_id=chat_window_id)).all()
    if all_chat_recorder:
        all_chat_recorder.sort(key=instrument.get_time)
        list_chat_recorder = []
        for chat in all_chat_recorder:
            chat_recorder = {"content": chat.content}
            list_chat_recorder.append(chat_recorder)
        return flask.jsonify(code="200", data=list_chat_recorder)
    return flask.jsonify(code="400", data="")


@USER_BLUE_PRINT.route("/feedback", methods=['POST'])
@flask_login.login_required
def post_feedback():
    """
    上传反馈视图
    Returns:code
    200 表示成功
    400 表示失败

    """
    form = flask.request.get_json()
    user_id = form.get("user_id")
    content = form.get("content")
    code = "400"
    if user_id and content:
        try:
            feedback = module.FeedBack(user_id=user_id, content=content,
                                       feedback_date=datetime.date.today())
            extentions.DATABASE.session.add(feedback)
        except Exception as error:
            extentions.DATABASE.session.rollback()
            print("反馈失败！", error)
            # 插入错误日志
            error_log = module.ErrorLog(error_id=1)
            extentions.DATABASE.session.add(error_log)
            extentions.DATABASE.session.commit()
            return flask.jsonify(code=code)
        extentions.DATABASE.session.commit()
        code = "200"
        return flask.jsonify(code=code)
    return flask.jsonify(code=code)


@USER_BLUE_PRINT.route("/get_advertising", methods=['GET'])
@flask_login.login_required
def get_advertising():
    """
    获取广告图片视图
    Returns:
    广告图片
    获取失败则返回code和一个message
    """
    path = "aaa_file/advertise"
    for dir_name, listdir, files in os.walk(path):
        for file in files:
            if file.startswith("aaa_advertise"):
                target = os.path.join(dir_name, file)
                return flask.send_file(target)
    return flask.jsonify(code="400", message="获取图片失败！")


@USER_BLUE_PRINT.route("/get_advertise_state", methods=['GET'])
@flask_login.login_required
def get_advertise_state():
    user_id = flask.request.args.get("user_id")
    code = "400"
    advertise_state = False
    if user_id:
        user = module.User.query.get(user_id)
        advertise_state = user.advertise_state
        code = "200"
    return flask.jsonify(code=code, advertise_state=advertise_state)


# TODO 推送消息到前端需要指定一个会话，目前由前端进行判断
@USER_BLUE_PRINT.route("/top_up", methods=['POST'])
@flask_login.login_required
def top_up():
    """
    充值确认视图
    确认用户扫描二维码后，完成充值并且推送消息到前端
    Returns:渲染一个提示界面

    """
    form = flask.request.get_json()
    user_id = form.get("user_id")
    top_up_id = form.get("type")
    user = module.User.query.get(user_id)
    top_up_type = module.TopUpType.query.get(top_up_id)
    code = "200"
    # 插入充值订单
    try:
        top_up_order = module.TopUpOrder(user_id=user_id, type_id=top_up_id)
        extentions.DATABASE.session.add(top_up_order)
        extentions.DATABASE.session.commit()
    except Exception as error:
        extentions.DATABASE.session.rollback()
        # 插入错误日志
        error_log = module.ErrorLog(error_id=1)
        extentions.DATABASE.session.add(error_log)
        extentions.DATABASE.session.commit()
        code = "400"
        print("充值订单插入失败！", error)
        return flask.jsonify(code=code)
    # vip用户续vip
    # 将问答次数回满
    if user and top_up_type:
        if user.user_type_id == 4:
            user.vip_time_raiming += top_up_type.valid_time
            user.current_query_times = 30
        # 普通用户成为vip用户
        # 将问答次数回满
        elif user.user_type_id == 3:
            user.user_type_id = 4
            user.vip_time_raiming = top_up_type.valid_time
            user.query_times = 30
            user.current_query_times = 30
        user.limit = False
        extentions.DATABASE.session.commit()
    return flask.jsonify(code=code)


@USER_BLUE_PRINT.route("/get_query_times", methods=['GET'])
@flask_login.login_required
def get_query_times():
    """
    获取用户的可询问次数以及当前剩余的询问次数
    Returns:
    code： 200 表示成功 400 表示失败
    all_query_times： 可询问的次数
    current_query_times： 当前剩余的询问次数
    """
    user_id = flask.request.args.get("user_id")
    code = "400"
    all_query_times = 0
    current_query_times = 0
    if user_id:
        user = module.User.query.get(user_id)
        if user:
            code = "200"
            all_query_times = user.query_times
            current_query_times = user.current_query_times
    return flask.jsonify(code=code, all_query_times=all_query_times,
                         current_query_times=current_query_times)


@USER_BLUE_PRINT.route("/get_vip_state", methods=['GET'])
@flask_login.login_required
def get_vip_state():
    """
    获取用户的vip状态
    Returns:code， state
    code 200 表示成功
         400 表示失败
    state False 表示不是vip
          True 表示是vip
    """
    user_id = flask.request.args.get("user_id")
    code = "400"
    state = False
    if user_id:
        user = module.User.query.get(user_id)
        if user:
            code = "200"
            state = True if user.vip_time_raiming > 0 else False
    return flask.jsonify(code=code, state=state)


@USER_BLUE_PRINT.route("/is_limit_login", methods=['GET'])
@flask_login.login_required
def check_limit_login():
    """
    判断用户是否被限制登录
    Returns:
    code 400表示获取失败
        200 表示获取成功
    is_limit True表示被限制
             False表示没有被限制
             None表示查询失败
    """
    code = "400"
    is_limit = False
    user_id = flask.request.args.get("user_id")
    if user_id:
        user = module.User.query.get(user_id)
        if user:
            if user.restriction_time > 0:
                is_limit = True
                code = "200"
                return flask.jsonify(code=code, is_limit=is_limit)
            else:
                code = "200"
                return flask.jsonify(code=code, is_limit=is_limit)
    return flask.jsonify(code=code, is_limit=None)


class CommenUser(object):
    """
    这是一般用户类
    不包含属性
    只拥有静态方法，用来实现用户的种种功能

    """

    @staticmethod
    def set_information(**kwargs):
        """设置用户信息
        根据传入的字典数据设置用户的昵称，性别信息
        Args:
            **kwargs:传入的为需要进行修改的个人信息字典

        Returns:
            修改成功返回 True
            修改失败则返回 False

        """
        user_id = kwargs.get("user_id")
        nickname = kwargs.get("nickname")
        sex = kwargs.get("sex")
        advertise_state = kwargs.get("advertise_state")
        user = module.User.query.get(user_id)
        if user:
            user.nickname = nickname
            user.sex = sex
            user.advertise_state = advertise_state
            extentions.DATABASE.session.commit()
            return True
        return False

    @staticmethod
    def get_information(user_id):
        """获取指定用户信息
        根据用户的id精确查询到用户并得到个人信息
        Args:
            user_id: 用户编号

        Returns:form字典对象
        包含用户的昵称，性别以及询问次数，以及用户头像图片在服务器上的路径
        其中code用来表示获取信息是否成功
        code 200 表示成功 400 表示失败
        """
        user = module.User.query.get(user_id)
        form = {"code": "400"}
        if user:
            form["code"] = "200"
            form["nickname"] = user.nickname
            form["mail_account"] = user.mail_account
            form["sex"] = user.sex
            form["query_times"] = user.query_times
            form["advertise_state"] = user.advertise_state
            form["vip_time"] = user.vip_time_raiming
        return form

    @staticmethod
    def change_password(user_id, new_password, old_password):
        """修改用户密码
        通过传入的用户的id查找用户对象并修改密码
        Args:
            old_password:  原密码
            user_id: 用户的id
            new_password: 用户的新密码

        Returns:布尔值
        True表示修改成功
        False表示修改失败，没有查询到对应的用户

        """
        user = module.User.query.get(user_id)
        code = "400"
        if user:
            if user.password != old_password:
                code = "401"
            else:
                user.password = new_password
                extentions.DATABASE.session.commit()
                code = "200"
        return code

    @staticmethod
    def search_all_group(user_id):
        """
        根据用户的id查询得到所有的分组信息并通过列表进行返回
        Args:
            user_id:

        Returns:form列表
        列表中包含了多个字典对象
        其中每个对象包含group_id，group_name
        """
        group_list = module.ChatWindowGroup.query.filter_by(user_id=user_id)
        form = []
        for group in group_list:
            json_data = {"group_id": group.group_id,
                         "group_name": group.group_name,
                         "judge": "true",
                         "change_group_name1": "true",
                         "change_group_name2": "false"}
            form.append(json_data)
        return form

    @staticmethod
    def search_all_window(user_id):
        """
        根据用户的编号查询所属的聊天窗口
        Args:
            user_id: 用户id编号

        Returns:form列表
        其中包含多个对象
        每个对象包含chat_window_id，chat_window_name， group_id

        """
        window_list = module.ChatWindow.query.filter_by(user_id=user_id).all()
        form = []
        if window_list:
            for window in window_list:
                json_data = {"chat_window_id": window.chat_window_id,
                             "chat_window_name": window.chat_window_name,
                             "group_id": window.group_id,
                             "change_window_name1": "true",
                             "change_window_name2": "false"}
                form.append(json_data)
        return form

    @staticmethod
    def add_chat_window(user_id, group_id):
        """
        添加新的聊天窗口
        Args:
            user_id:用户编号
            group_id: 窗口的编号

        Returns:
            添加失败时返回False和一个空字符串
            添加成功时返回True和新聊天窗口的id编号

        """
        chat_window = module.ChatWindow(
            chat_window_name="new chat",
            user_id=user_id,
            group_id=group_id
        )
        try:
            extentions.DATABASE.session.add(chat_window)
        except Exception as error:
            print("添加失败了", error)
            extentions.DATABASE.session.rollback()
            # 插入错误日志
            error_log = module.ErrorLog(error_id=1)
            extentions.DATABASE.session.add(error_log)
            extentions.DATABASE.session.commit()
            return False, ""
        extentions.DATABASE.session.commit()
        extentions.DATABASE.session.flush()
        return True, chat_window.chat_window_id

    @staticmethod
    def rename_chat_window(chat_window_id, chat_window_name):
        """
        重命名聊天窗口
        通过聊天窗口编号进行查找并修改名字
        Args:
            chat_window_id:
            chat_window_name:

        Returns:布尔值
        True 表示修改成功
        False 表示失败
        """
        chat_window = module.ChatWindow.query.get(chat_window_id)
        if chat_window:
            chat_window.chat_window_name = chat_window_name
            extentions.DATABASE.session.commit()
            return True
        return False

    @staticmethod
    def delete_chat_window(chat_window_id):
        """
        删除聊天窗口
        Args:
            chat_window_id: 聊天窗口编号

        Returns:布尔值
        True 表示成功
        False 表示失败
        """
        chat_window = module.ChatWindow.query.get(chat_window_id)
        try:
            extentions.DATABASE.session.delete(chat_window)
        except Exception as error:
            print("删除聊天窗口出错了", error)
            extentions.DATABASE.session.rollback()
            # 插入错误日志
            error_log = module.ErrorLog(error_id=1)
            extentions.DATABASE.session.add(error_log)
            extentions.DATABASE.session.commit()
            return False
        extentions.DATABASE.session.commit()
        return True

    @staticmethod
    def add_window_group(user_id, group_name="分组"):
        """
        增加聊天窗口分组
        Args:
            user_id: 用户编号
            group_name: 聊天分组的名字

        Returns:布尔值， 分组编号
        True 表示成功
        False 表示失败
        """
        group = module.ChatWindowGroup(user_id=user_id, group_name=group_name)
        try:
            extentions.DATABASE.session.add(group)
        except Exception as error:
            print("新增分组出错了！", error)
            extentions.DATABASE.session.rollback()
            # 插入错误日志
            error_log = module.ErrorLog(error_id=1)
            extentions.DATABASE.session.add(error_log)
            extentions.DATABASE.session.commit()
            return False, ""
        extentions.DATABASE.session.commit()
        extentions.DATABASE.session.flush()
        return True, group.group_id

    @staticmethod
    def rename_window_group(group_name, group_id):
        """
        重命名分组函数
        Args:
            group_name: 分组名称
            group_id:  分组编号

        Returns:布尔值
        True 表示成功
        False 表示失败

        """
        group = module.ChatWindowGroup.query.get(group_id)
        if group:
            group.group_name = group_name
            extentions.DATABASE.session.commit()
            return True
        return False

    @staticmethod
    def delete_window_group(group_id):
        """
        删除分组函数
        删除分组的同时删除其中的聊天窗口
        Args:
            group_id:

        Returns:布尔值
        True 表示删除成功
        False 表示失败
        """
        # TODO 可以在聊天分组表中添加关系
        group = module.ChatWindowGroup.query.get(group_id)
        if group:
            try:
                windows = module.ChatWindow.query.filter_by(group_id=group_id)
                if windows:
                    for window in windows:
                        extentions.DATABASE.session.delete(window)
                extentions.DATABASE.session.delete(group)
            except Exception as error:
                print("删除聊天窗口出错了！", error)
                extentions.DATABASE.session.rollback()
                # 插入错误日志
                error_log = module.ErrorLog(error_id=1)
                extentions.DATABASE.session.add(error_log)
                extentions.DATABASE.session.commit()
                return False
            extentions.DATABASE.session.commit()
            return True
        else:
            return False

    @staticmethod
    def change_head_portrait(user_id, file_path):
        """
        修改用户头像函数
        Args:
            user_id: 用户编号
            file_path: 头像保存的路径

        Returns:布尔值
        True 表示修改成功
        False 表示修改失败

        """
        user = module.User.query.get(user_id)
        if user:
            # 获取原来头像的信息
            old_head_portrait_id = user.head_portrait_id
            old_head_portrait = module.HeadPortrait.query.get(
                old_head_portrait_id)
            old_path = old_head_portrait.path
            # 创建新头像
            head_portrait = module.HeadPortrait(path=file_path)
            extentions.DATABASE.session.add(head_portrait)
            extentions.DATABASE.session.commit()
            extentions.DATABASE.session.flush()
            user.head_portrait_id = head_portrait.head_portrait_id
            # 删除原来头像的记录以及图片
            if old_head_portrait_id != 1 and os.path.exists(old_path):
                print("旧头像删除成功！")
                os.remove(old_path)
                extentions.DATABASE.session.delete(old_head_portrait)
            extentions.DATABASE.session.commit()
            return True
        return False
