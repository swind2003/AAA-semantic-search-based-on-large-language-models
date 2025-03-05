#!/usr/bin/env python3.10.13
"""对前端页面提供的登录系统api.

Copyright 2023 Li Jinhua.
License(GPL)
Author: Li Jinhua
"""
import random
import flask
import flask_mail
import flask_login

import extentions
import module
from blue_prints import common_user
# /login_system
LOGIN_BP = flask.Blueprint("login_system", __name__,
                           url_prefix="/login_system")


@LOGIN_BP.route("/log_in", methods=['GET', 'POST'])
def log_in():
    """
    视图函数--登录
    code对应的含义:
    200: 登录成功
    400: 用户名或密码错误
    401: 用户目前被限制登录
    :return:
    """
    front_datas = flask.request.get_json()
    print(front_datas)
    mail_account = front_datas.get("mail_account")
    password = front_datas.get("password")
    # 200: 登录成功
    # 400: 用户名或密码错误
    # print(mail_account, password)
    code, user = LoginSystem.log_in(mail_account=mail_account,
                                    password=password)
    user_id = -1
    user_type_id = -1
    head_portrait_id = ""
    mail_account = ""
    nickname = ""
    sex = ""
    advertise_state = False
    restriction_time = -1
    if (code == "200" or "401") and user:
        user_id = user.user_id
        user_type_id = user.user_type_id
        head_portrait_id = user.head_portrait_id
        mail_account = user.mail_account
        nickname = user.nickname
        sex = user.sex
        restriction_time = user.restriction_time
        advertise_state = user.advertise_state
        # print(restriction_time)

    if code == "200" and user:
        flask_login.login_user(user, remember=True)
        try:
            # 可能出现意外错误
            # 创建 inserted_login_log
            inserted_login_log = module.LoginLog(user_id=user.user_id)
            extentions.DATABASE.session.add(inserted_login_log)
            extentions.DATABASE.session.commit()
            # return True
        except Exception as error:
            print("插入登录日志时出现意外错误\n", error)
            error_log = module.ErrorLog(
                error_id=1
            )
            extentions.DATABASE.session.add(error_log)
            extentions.DATABASE.session.commit()
    # return flask.jsonify({
    #     "code": code,
    #     "user_id": user_id,
    #     "user_type_id": user_type_id,
    #     "head_portrait_id": head_portrait_id,
    #     "mail_account": mail_account,
    #     "nickname": nickname,
    #     "sex": sex,
    #     "restriction_time": restriction_time,
    #     "advertise_state": advertise_state
    # })
    response = flask.make_response(flask.jsonify({
        "code": code,
        "user_id": user_id,
        "user_type_id": user_type_id,
        "head_portrait_id": head_portrait_id,
        "mail_account": mail_account,
        "nickname": nickname,
        "sex": sex,
        "restriction_time": restriction_time,
        "advertise_state": advertise_state
    }))
    response.set_cookie("user_id", str(user_id))
    return response


@LOGIN_BP.route("/log_out", methods=['GET', 'POST'])
@flask_login.login_required
def log_out():
    """
    视图函数--登出
    code对应的含义:
    200: 成功
    400: 失败
    :return:
    """
    front_datas = flask.request.get_json()
    user_id = front_datas.get("user_id")
    try:
        # 可能出现意外错误
        # 创建 inserted_login_log
        inserted_logout_log = module.LogoutLog(user_id=user_id)
        extentions.DATABASE.session.add(inserted_logout_log)
        extentions.DATABASE.session.commit()
        code = "200"
        # flask_login.logout_user()
    except Exception as error:
        code = "400"
        print("插入登录日志时出现意外错误\n", error)
        error_log = module.ErrorLog(
            error_id=1
        )
        extentions.DATABASE.session.add(error_log)
        extentions.DATABASE.session.commit()

    return flask.jsonify({
        "code": code
    })


@LOGIN_BP.route("/register_verification_code", methods=['GET', 'POST'])
def register_verification_code():
    """
    视图函数--注册时发送验证码
    code对应的含义:
    200: 验证码已发送
    400: 验证码发送失败
    401: 该邮箱已注册
    :return:
    """
    front_datas = flask.request.get_json()
    mail_account = front_datas.get("mail_account")
    code, verification_code = LoginSystem.register_verification_code(
        mail_account=mail_account)

    return flask.jsonify({
        "code": code,
        "mail_account": mail_account,
        "verification_code": verification_code
    })


@LOGIN_BP.route("/register", methods=['GET', 'POST'])
def register():
    """
    视图函数--验证码通过后添加注册用户
    code对应的含义:
    200: 已成功注册
    400: 注册失败
    :return:
    """
    front_datas = flask.request.get_json()
    mail_account = front_datas.get("mail_account")
    password = front_datas.get("password")
    # print(mail_account)
    # print(password)
    code = LoginSystem.register(
        mail_account=mail_account, password=password)

    return flask.jsonify({
        "code": code
    })


@LOGIN_BP.route("/retrieve_verification_code", methods=['GET', 'POST'])
def retrieve_verification_code():
    """
    视图函数--找回密码时发送验证码
    code对应的含义:
    200: 验证码已发送
    400: 验证码发送失败
    401: 该邮箱未注册过
    :return:
    """
    front_datas = flask.request.get_json()
    mail_account = front_datas.get("mail_account")
    print(mail_account)
    code, verification_code = LoginSystem.retrieve_verification_code(
        mail_account=mail_account)

    return flask.jsonify({
        "code": code,
        "mail_account": mail_account,
        "verification_code": verification_code
    })


@LOGIN_BP.route("/retrieve_password", methods=['GET', 'POST'])
def retrieve_password():
    """
    视图函数--验证码通过后修改用户密码
    code对应的含义:
    200: 已成功修改
    400: 修改失败
    :return:
    """
    front_datas = flask.request.get_json()
    mail_account = front_datas.get("mail_account")
    password = front_datas.get("password")
    code = LoginSystem.retrieve_password(
        mail_account=mail_account, password=password)

    return flask.jsonify({
        "code": code
    })


class LoginSystem(object):
    """
    登录系统相关功能
    """
    @staticmethod
    def log_in(mail_account, password):
        """
        登录验证
        :param mail_account: 邮箱
        :param password: 密码
        :return:
        """
        user = module.User.query.filter_by(mail_account=mail_account).first()
        if user and user.password == password:
            if user.restriction_time > 0:
                return "401", user
            return "200", user
        else:
            return "400", None

    @staticmethod
    def send_verification_code(mail_account):
        """
        发送验证码
        :param mail_account:
        :return:
        """
        verification_code = random.randint(10000, 99999)
        verification_code = str(verification_code)
        # print(verification_code)
        message = flask_mail.Message(
            subject="验证码",
            recipients=[mail_account],
            body=f"您的验证码是:\n{verification_code}")
        try:
            result = extentions.MAIL.send(message)
        except Exception as error:
            # 验证码发送失败
            result = "400"
            print("验证码发送失败\n", error)
            error_log = module.ErrorLog(
                error_id=4
            )
            extentions.DATABASE.session.add(error_log)
            extentions.DATABASE.session.commit()
            # print(result)
        if not result:
            # 验证码发送成功
            code = "200"
            return code, verification_code
        else:
            # 验证码发送失败
            code = result
            verification_code = "00000"
            return code, verification_code

    @staticmethod
    def register_verification_code(mail_account):
        """
        注册时发送验证码
        :param mail_account:
        :return:
        """
        user = module.User.query.filter_by(mail_account=mail_account).first()
        if user:
            # 邮箱已注册过
            code = "401"
            verification_code = "00000"
            return code, verification_code
        else:
            code, verification_code = \
                LoginSystem.send_verification_code(mail_account)
            return code, verification_code

    @staticmethod
    def register(mail_account, password):
        """
        验证码通过后添加注册用户
        :param mail_account:
        :param password:
        :return:
        """
        user = module.User.query.filter_by(mail_account=mail_account).first()
        if user:
            return "400"
        else:
            try:
                # 可能出现意外错误
                # 创建user
                user = module.User(mail_account=mail_account, password=password)
                extentions.DATABASE.session.add(user)
                extentions.DATABASE.session.commit()
            except Exception as error:
                print("添加注册用户到数据库出现意外错误\n", error)
                error_log = module.ErrorLog(
                    error_id=1
                )
                extentions.DATABASE.session.add(error_log)
                extentions.DATABASE.session.commit()
                return "400"
        # 创建默认窗口分组
        extentions.DATABASE.session.flush()
        success = common_user.CommenUser.add_window_group(user.user_id,
                                                          "默认分组")
        if success:
            return "200"
        return "400"

    @staticmethod
    def retrieve_verification_code(mail_account):
        """
        找回密码时发送验证码
        :param mail_account:
        :return:
        """
        # print(mail_account)
        user = module.User.query.filter_by(mail_account=mail_account).first()
        if not user:
            # 邮箱未注册过
            code = "401"
            verification_code = "00000"
            return code, verification_code
        else:
            code, verification_code = \
                LoginSystem.send_verification_code(mail_account)
            return code, verification_code

    @staticmethod
    def retrieve_password(mail_account, password):
        """
        修改用户密码
        Args:
            mail_account:
            password:

        Returns:

        """
        user = module.User.query.filter_by(mail_account=mail_account).first()
        if not user:
            return "400"
        else:
            try:
                # 可能出现意外错误
                user.password = password
                extentions.DATABASE.session.commit()
            except Exception as error:
                print("修改用户密码出现意外错误\n", error)
                error_log = module.ErrorLog(
                    error_id=1
                )
                extentions.DATABASE.session.add(error_log)
                extentions.DATABASE.session.commit()
                return "400"
        return "200"
