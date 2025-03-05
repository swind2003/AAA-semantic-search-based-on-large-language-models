#!/usr/bin/env python3.10.13
"""This is the Administrator Blueprint.

Copyright 2023 ZheYun Liu & Yan Wang
License(GPL)
Author: ZheYun Liu & Yan Wang
"""

import json
import os

import flask
import flask_login
import requests
import sqlalchemy
import extentions
import module
import instrument

ADMINISTRATOR_BP = flask.Blueprint(
    "administrator", __name__, url_prefix="/administrator")


@ADMINISTRATOR_BP.route("/set_company_info", methods=["POST"])
@flask_login.login_required
def set_company_info():
    """Functions to set enterprise information.

    Returns:
        200 if the file was saved successfully and 400 otherwise.
    """
    my_args = flask.request.get_json()
    contact_way = my_args.get("contact_way")
    user_agreement = my_args.get("user_agreement")
    code = "200" if Manager.set_enterprise_information(
        contact_way=contact_way,
        user_agreement=user_agreement
    ) else "400"
    return flask.jsonify({"code": code})


@ADMINISTRATOR_BP.route("/get_company_info", methods=["GET"])
@flask_login.login_required
def get_company_info():
    """Functions to set enterprise information.

    Returns:
        200 if the file was saved successfully and 400 otherwise.
    """
    company_info = Manager.get_enterprise_information()
    return flask.jsonify(data=company_info)


@ADMINISTRATOR_BP.route("/get_head_portrait", methods=['GET'])
@flask_login.login_required
def get_head_portrait():
    """
    获取头像视图
    Returns:
    成功则将头像文件发送到前端
    失败则放回code 400 并提示相应信息
    """
    user_id = flask.request.args.get('user_id')
    user = module.User.query.get(user_id)
    if user:
        head_portrait = module.HeadPortrait.query.get(user.head_portrait_id)
        if head_portrait:
            path = head_portrait.path
            return flask.send_file(path)
    return flask.jsonify(code="400", message="获取头像出错")


# TODO(ZheYun Liu): Returns information and avatars for all users.
@ADMINISTRATOR_BP.route("/get_all_user", methods=["GET"])
@flask_login.login_required
def get_all_user():
    """A function to get information about all users.

    Returns:
        Returns the information for all users as two json list.
    """
    my_information = Manager.get_all_user()
    return flask.jsonify(data=my_information)


# TODO(ZheYun Liu): Returns the filtered user profile and avatar.
@ADMINISTRATOR_BP.route("/search_user", methods=["GET"])
@flask_login.login_required
def search_user():
    """A function to get information about all users.

    Returns:
        Returns the information for filtered users as two json list.
    """
    mail_account = ""
    nickname = ""
    try:
        mail_account = flask.request.args.get("mail_account")
        nickname = flask.request.args.get("nickname")
    except ValueError:
        print("无法解析为json对象")
    except TypeError:
        print("无法转换为python对象")
    finally:
        print(mail_account)
        print(nickname)
    my_information = Manager.search_user(
        mail_account=mail_account,
        nickname=nickname
    )
    return flask.jsonify(data=my_information)


@ADMINISTRATOR_BP.route("/delete_user", methods=["DELETE"])
@flask_login.login_required
def delete_user():
    """Delete a user's function.

    Returns:
        Returns 200 on success, 400 otherwise.
    """
    my_args = flask.request.args
    user_id = my_args.get("user_id")
    code = "200" if Manager.delete_user(user_id) else "400"
    return flask.jsonify({"code": code})


@ADMINISTRATOR_BP.route("/restrict_login", methods=["POST"])
@flask_login.login_required
def restrict_login():
    """Limit the number of days a user has logged in.

    Returns:
        Returns 200 on success, 400 otherwise.
    """
    my_args = flask.request.get_json()
    user_id = my_args.get("user_id")
    number_time = int(my_args.get("number_time"))
    code = "200" if Manager.limit_login(user_id, number_time) else "400"
    return flask.jsonify({"code": code})


@ADMINISTRATOR_BP.route("/restrict_query", methods=["POST"])
@flask_login.login_required
def restrict_query():
    """Limit the number of questions the user asks.

    Returns:
        Returns 200 on success, 400 otherwise.
    """
    my_args = flask.request.get_json()
    user_id = my_args.get("user_id")
    query_times = int(my_args.get("query_times"))
    code = "200" if Manager.limit_access(user_id, query_times) else "400"
    return flask.jsonify({"code": code})


@ADMINISTRATOR_BP.route("/log/get_all_log", methods=["GET"])
@flask_login.login_required
def get_all_log():
    """Returns all user logins and logouts.

    Returns:
        Returns a list with dictionary elements. For example:
        {
            "mail_account": ...,
            "timing": ...,
            "type": "1"
        }
    """
    my_log = Manager.get_logging_log()
    print(my_log)
    return flask.jsonify(data=my_log)


@ADMINISTRATOR_BP.route("/log/get_error_log", methods=["GET"])
@flask_login.login_required
def get_error_log():
    """Getting error logs.

    Returns:
        Returns a list with dictionary elements. For example:
        {
            "mail_account": ...,
            "timing": ...,
            "error_code": ...
        }
    """
    my_log = Manager.get_all_error_log()
    print(my_log)
    return flask.jsonify(data=my_log)


# @ADMINISTRATOR_BP.route("/log/export_log", methods=["GET"])
# def export_log():
#     """Export logout logs.
#
#     Returns:
#         Return the xlsx file.
#     """
#     my_log = Manager.get_logging_log()
#     my_data_frame = pd.DataFrame(my_log)
#     file_path = "aaa_file/logging_log.xlsx"
#     my_data_frame.to_excel(file_path, index=False)
#     return flask.send_file(file_path, as_attachment=True)
# @ADMINISTRATOR_BP.route("/log/export_error_log", methods=["GET"])
# def export_error_log():
#     """Export error logs.
#
#     Returns:
#         Return the xlsx file.
#     """
#     my_log = Manager.get_all_error_log()
#     my_data_frame = pd.DataFrame(my_log)
#     file_path = "aaa_file/error_log.xlsx"
#     my_data_frame.to_excel(file_path, index=False)
#     return flask.send_file(file_path, as_attachment=True)


@ADMINISTRATOR_BP.route("/set_advertising", methods=['POST'])
@flask_login.login_required
def set_advertise_picture():
    """
    设置广告图片视图
    Returns:code
    200 表示设置成功
    400 表示设置失败

    """
    file = flask.request.files.get('advertise')
    code = "400"
    if file:
        file_name = file.filename
        if instrument.determine_suffix(file_name):
            path = 'aaa_file/advertise/aaa_advertise_picture.jpg'
            file.save(path)
            code = "200"
    return flask.jsonify(code=code)


@ADMINISTRATOR_BP.route("/change_url_link", methods=['POST'])
@flask_login.login_required
def change_url_link():
    """
    修改广告跳转的链接
    Returns: code
    code 200 表示成功
    400 表示失败
    """
    url = flask.request.get_json().get("url")
    code = "400"
    if url:
        try:
            with open("aaa_file/advertise/url_link.json", "r+") as file:
                content = json.load(file)
                content["url"] = url
                file.seek(0)
                file.truncate()
                json.dump(content, file)
                code = "200"
        except IOError as error:
            print("修改链接出错！", error)
            # 插入错误日志
            error_log = module.ErrorLog(error_id=3)
            extentions.DATABASE.session.add(error_log)
            extentions.DATABASE.session.commit()
    return flask.jsonify(code=code)


@ADMINISTRATOR_BP.route("/get_url_link", methods=['GET'])
@flask_login.login_required
def get_url_link():
    """
    获取广告跳转链接
    Returns:code data
    code 200 表示成功
         400 表示失败
    data中有url数据
    """
    content = None
    code = "400"
    try:
        with open("aaa_file/advertise/url_link.json", "r") as file:
            content = json.load(file)
            code = "200"
    except IOError as error:
        print("读取链接失败", error)
        # 插入错误日志
        error_log = module.ErrorLog(error_id=3)
        extentions.DATABASE.session.add(error_log)
        extentions.DATABASE.session.commit()
    return flask.jsonify(code=code, data=content)


@ADMINISTRATOR_BP.route("/check_feedback", methods=['GET'])
@flask_login.login_required
def get_all_feedback():
    """
    获取所有反馈视图
    Returns:code 200 表示成功
                400  表示失败
            data 成功则包含用户反馈的多个对象
                 失败则包含一个空

    """
    is_checked = int(flask.request.args.get("is_checked", "-1"))
    start_date = flask.request.args.get("start_date")
    end_date = flask.request.args.get("end_date")
    print(start_date, end_date)
    if is_checked in (0, 1):
        data = Manager.get_feedback(is_checked=is_checked,
                                    start_date=start_date,
                                    end_date=end_date)
        return flask.jsonify(code="200", data=data)
    return flask.jsonify(code="400", data={})


@ADMINISTRATOR_BP.route("/set_checked", methods=['POST'])
@flask_login.login_required
def set_feedback_checked():
    """
    设置用户反馈已阅
    Returns:
    code 200 设置成功
         400 设置失败
    """
    feedback_id = flask.request.get_json().get("feedback_id")
    code = "400"
    if feedback_id:
        feedback = module.FeedBack.query.get(feedback_id)
        feedback.is_checked = not feedback.is_checked
        extentions.DATABASE.session.commit()
        code = "200"
    return flask.jsonify(code=code)


@ADMINISTRATOR_BP.route("/check_order", methods=['GET'])
@flask_login.login_required
def get_order():
    """
    获取充值订单的视图
    Returns:json格式数据
    data中为一个列表，其中列表中包含有多个字典对象，字典中包含订单的相关信息
    """
    start_date = flask.request.args.get("start_date")
    end_date = flask.request.args.get("end_date")
    list_order = Manager.get_all_order(start_date, end_date)
    print(list_order)
    return flask.jsonify(data=list_order)


@ADMINISTRATOR_BP.route("/get_old_advertise", methods=['GET'])
@flask_login.login_required
def get_old_advertise():
    """
    获取设置了的广告图片
    Returns:
    成功则将广告图片发送到前端
    失败则返回code以及提示信息
    """
    path = "aaa_file/advertise"
    for dir_name, listdir, files in os.walk(path):
        for file in files:
            if file.startswith("aaa_advertise"):
                target = os.path.join(dir_name, file)
                return flask.send_file(target)
    return flask.jsonify(code="400", message="获取图片失败！")


class Manager(object):
    """This is the class that defines the administrator functionality.

    All the methods here are static methods.
    """

    @staticmethod
    def set_enterprise_information(
            contact_way: str, user_agreement: str) -> bool:
        """Save enterprise information to a json file.

        Args:
            contact_way(str): How to contact us.
            user_agreement(str): Information the user needs to know.

        Returns:
            True if the file was saved successfully and False otherwise.
        """
        try:
            with open("aaa_file/enterprise_information.json", "w") as file:
                context = {
                    "contact_way": contact_way,
                    "user_agreement": user_agreement
                }
                json.dump(context, file)
        except OSError:
            print("Enterprise information written error!")
            # 插入错误日志
            error_log = module.ErrorLog(error_id=3)
            extentions.DATABASE.session.add(error_log)
            extentions.DATABASE.session.commit()
            return False
        else:
            return True

    @staticmethod
    def get_enterprise_information() -> dict:
        """Get enterprise information from a json file.

        Returns:
            The enterprise information in dict format.
        """
        try:
            content = {}
            with open("aaa_file/enterprise_information.json", "r") as file:
                content = json.load(file)
        except OSError:
            print("Enterprise information written error!")
            # 插入错误日志
            error_log = module.ErrorLog(error_id=3)
            extentions.DATABASE.session.add(error_log)
            extentions.DATABASE.session.commit()
        finally:
            return content

    @staticmethod
    def limit_access(user_id: str, query_times: int) -> bool:
        """Limit the number of user visits.

        Args:
            user_id(str): The user id in the DATABASE.
            query_times(int): The number of accesses to limit the user.

        Returns:
            Returns True on success, False otherwise.
        """
        user = module.User.query.filter_by(user_id=user_id).first()
        if not user:
            print("The user was not found.")
            return False
        else:
            if query_times < 8:
                user.limit = 1
                user.query_times = query_times
                user.current_query_times = query_times
            else:
                user.limit = 0
                if user.vip_time_raiming > 0:
                    user.query_times = 30
                    user.current_query_times = 30
                else:
                    user.query_times = query_times
                    user.current_query_times = query_times
            extentions.DATABASE.session.commit()
            return True

    @staticmethod
    def limit_login(user_id: str, number_time: int) -> bool:
        """A function that prevents a user from logging in.

        Args:
            user_id(str): The user id in the DATABASE.
            number_time(int): Number of days a user is banned from logging in.

        Returns:
            Returns True on success, False otherwise.
        """
        user = module.User.query.filter_by(user_id=user_id).first()
        if not user:
            print("The user was not found.")
            return False
        else:
            user.restriction_time = number_time
            extentions.DATABASE.session.commit()
            return True

    @staticmethod
    def delete_user(user_id: str) -> bool:
        """A function to delete a user.

        Args:
            user_id(str): The user id in the DATABASE.

        Returns:
            Returns True on success, False otherwise.
        """
        user = module.User.query.filter_by(user_id=user_id).first()
        if not user:
            print("The user was not found.")
            return False
        else:
            extentions.DATABASE.session.delete(user)
            extentions.DATABASE.session.commit()
            return True

    # TODO(ZheYun Liu): Sends the user's info and avatar to the frontend.
    @staticmethod
    def get_all_user() -> list:
        """A function to retrieve all users.

        Returns:
            Returns the user's information and avatar in list format.
        """
        users = module.User.query.filter(sqlalchemy.or_(
            module.User.user_type_id == 3,
            module.User.user_type_id == 4)).all()
        if not users:
            print("No user.")
            return []
        else:
            my_info = []
            for user in users:
                temp = {
                    "user_id": user.user_id,
                    "is_vip": "是" if user.vip_time_raiming > 0 else "否",
                    "nickname": user.nickname,
                    "mail_account": user.mail_account,
                    "sex": user.sex,
                    "if_login_limit": (
                        "true" if user.restriction_time > 0 else "false"),
                    "if_times_limit": "true" if user.limit == 1 else "false",
                }
                my_info.append(temp)
            return my_info

    # TODO(ZheYun Liu): Send the user's information and avatar to the frontend
    @staticmethod
    def search_user(mail_account: str, nickname: str) -> list:
        """A function to find a user by email or nickname.

        Args:
            mail_account(str): The user's email account.
            nickname(str): The user's nickname.

        Returns:
            A list of filtered users.
        """
        original_information = Manager.get_all_user()
        if not mail_account and nickname:
            user_information = [
                user for user in original_information
                if user["nickname"] == nickname
            ]
        elif mail_account and not nickname:
            user_information = [
                user for user in original_information
                if user["mail_account"] == mail_account
            ]
        elif not mail_account and not nickname:
            user_information = original_information
        else:
            user_information = [
                user for user in original_information
                if user["mail_account"] == mail_account or user[
                    "nickname"] == nickname
            ]
        return user_information

    @staticmethod
    def get_all_log(log_type: str) -> list:
        """A function to view the access logs.

        Returns:
            Returns a list of all logs in dictionary format,
            or an empty list if there are no logs.
        """
        if log_type == "login":
            logs = module.LoginLog.query.all()
        elif log_type == "logout":
            logs = module.LogoutLog.query.all()
        elif log_type == "error":
            logs = module.ErrorLog.query.all()
        else:
            print("The only arguments expected are 'login', "
                  "'logout' and 'error'.")
            raise ValueError("Invalid input value.")
        my_log = []
        if not logs:
            return my_log
        for every_log in logs:
            if log_type == "error":
                timing = str(every_log.error_time)
                error_type = module.ErrorType.query.get(every_log.error_id)
                error_code = error_type.error_code
                error_description = error_type.error_description
                temp = {
                    "timing": timing,
                    "error_code": error_code,
                    "error_description": error_description
                }
                my_log.append(temp)
            elif log_type == "logout":
                user = module.User.query.get(every_log.user_id)
                mail_account = user.mail_account
                timing = str(every_log.logout_time)
                temp = {
                    "mail_account": mail_account,
                    "timing": timing,
                    "type": "登出"
                }
            else:
                user = module.User.query.get(every_log.user_id)
                mail_account = user.mail_account
                timing = str(every_log.log_time)
                temp = {
                    "mail_account": mail_account,
                    "timing": timing,
                    "type": "登入"
                }
            my_log.append(temp)
        return my_log

    @staticmethod
    def get_logging_log() -> list:
        """A function to view the login and logout logs of all users.

        Returns:
            Returns a list of all logs in dictionary format,
            or an empty list if there are no logs. For example:
            {
                "mail_account": mail_account,
                "timing": year-month-day-hour-minute-second,
                "type": 0
            }
        """
        login_log = []
        logout_log = []
        try:
            login_log = Manager.get_all_log("login")
            logout_log = Manager.get_all_log("logout")
        except ValueError:
            print("The function is used incorrectly.")
        finally:
            my_log = login_log + logout_log
            my_log = sorted(my_log, key=lambda x: x["timing"], reverse=True)
            print(my_log)
            return my_log

    @staticmethod
    def get_all_error_log() -> list:
        """A function to get all error logs.

        Returns:
            Returns a list of all logs in dictionary format,
            or an empty list if there are no logs. For example:
            {
                "mail_account": mail_account,
                "timing": year-month-day-hour-minute-second,
                "error_code": "aaa"
                "error_description": "hhh"
            }
        """
        error_log = []
        try:
            error_log = Manager.get_all_log("error")
        except ValueError:
            print("The function is used incorrectly.")
        finally:
            error_log = sorted(
                error_log, key=lambda x: x["timing"], reverse=True)
            print(error_log)
            return error_log

    @staticmethod
    def get_feedback(is_checked, start_date=None, end_date=None):
        """
        获取反馈函数
        依据传入的参数获取相应的用户反馈
        Args:
            is_checked: 已查看的还是未查看的
            start_date:  起始日期
            end_date: 结束日期

        Returns:一个list其中list中包含有多个字典对象
        每个字典对象中包含用户反馈相关的多个信息

        """
        list_feedback = []
        # 获取所有用户反馈
        if not start_date and not end_date:
            list_feedback = (module.FeedBack.query.
                             filter_by(is_checked=is_checked).all())
        # 获取指定日期区间的用户反馈
        elif start_date and not end_date:
            list_feedback = (
                module.FeedBack.query.
                filter(sqlalchemy.and_(
                    module.FeedBack.is_checked == is_checked,
                    module.FeedBack.feedback_date >= start_date)).all())
        elif end_date and not start_date:
            list_feedback = (
                module.FeedBack.query.
                filter(sqlalchemy.and_(
                    module.FeedBack.is_checked == is_checked,
                    module.FeedBack.feedback_date <= end_date)).all())
        elif start_date and end_date:
            list_feedback = (
                module.FeedBack.query.
                filter(sqlalchemy.and_(
                    module.FeedBack.is_checked == is_checked,
                    module.FeedBack.feedback_date >= start_date,
                    module.FeedBack.feedback_date <= end_date)).all())
        list_feedback.sort(key=instrument.get_date, reverse=True)
        list_dict_feedback = []
        for feedback in list_feedback:
            user = module.User.query.get(feedback.user_id)
            data = {"feedback_id": feedback.feedback_id,
                    "is_checked": feedback.is_checked,
                    "nickname": user.nickname,
                    "mail_account": user.mail_account,
                    "date": str(feedback.feedback_date),
                    "content": feedback.content}
            list_dict_feedback.append(data)
        return list_dict_feedback

    @staticmethod
    def get_all_order(start_date=None, end_date=None):
        """
        获取所有订单数据
        Args:
            start_date: 起始日期
            end_date: 结束日期

        Returns: list_order列表，列表中包含了多个字典对象
        字典对象中包含了订单相关的信息
        {
            nickname 昵称
            mail_account 邮箱
            timestamp 时间日期
            type 充值类型
            price 价格
        }

        """
        all_order = []
        if not start_date and not end_date:
            all_order = module.TopUpOrder.query.all()
        elif start_date and not end_date:
            start_date += " 00:00:00"
            all_order = (module.TopUpOrder.query.
                         filter(module.TopUpOrder.order_time >= start_date).
                         all())
        elif end_date and not start_date:
            end_date += " 23:59:59"
            all_order = (module.TopUpOrder.query.
                         filter(module.TopUpOrder.order_time <= end_date).
                         all())
        elif end_date and start_date:
            start_date += " 00:00:00"
            end_date += " 23:59:59"
            all_order = (
                module.TopUpOrder.query.
                filter(sqlalchemy.and_(
                    module.TopUpOrder.order_time >= start_date,
                    module.TopUpOrder.order_time <= end_date)).all())
        all_order.sort(key=instrument.get_order_time, reverse=True)
        dict_type = instrument.change_to_dict()
        list_order = []
        for order in all_order:
            user = module.User.query.get(order.user_id)
            dict_order = {
                "mail_account": user.mail_account,
                "order_time": str(order.order_time),
                "type": dict_type.get(str(order.type_id))[0],
                "price": dict_type.get(str(order.type_id))[1]
            }
            list_order.append(dict_order)
        print(end_date, start_date, list_order)
        return list_order
