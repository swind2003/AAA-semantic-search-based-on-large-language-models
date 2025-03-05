#!/usr/bin/env python3.10.13
"""对前端页面提供的vip用户api.

Copyright 2023 Li Jinhua & Yan Wang.
License(GPL)
Author: Li Jinhua & Yan Wang
"""
import os

import flask_login
import requests
import flask

import extentions
import module

# /vip_user
VIP_USER_BP = flask.Blueprint("vip_user", __name__, url_prefix="/vip_user")


@VIP_USER_BP.route("/create_user_role", methods=['GET', 'POST'])
@flask_login.login_required
def create_user_role():
    """
    视图函数-创建用户自定义角色
    code对应的含义:
    200: 成功
    400: 失败
    :return:
    """
    user_id = flask.request.form.get("user_id")
    role_name = flask.request.form.get("role_name")
    description = flask.request.form.get("description")
    divergency = 1
    module_name = "gpt-3.5-turbo"
    module_api = "https://23w5971n67.goho.co/"
    if module_name == "gpt-3.5-turbo":
        module_api = "https://23w5971n67.goho.co/"
    prompt = flask.request.form.get("prompt")
    head_portrait = flask.request.files.get('head_portrait')
    files = flask.request.files.getlist("files")
    # 在数据库中生成用户自定义角色
    user_role = module.UserRole(
        user_id=user_id,
        role_name=role_name,
        head_portrait_id=None,
        description=description,
        divergency=divergency,
        module_name=module_name,
        module_api=module_api,
        prompt=prompt
    )
    try:
        extentions.DATABASE.session.add(user_role)
        extentions.DATABASE.session.commit()
        extentions.DATABASE.session.flush()
        # 指定文件夹路径
        doc_dir = VIPUser.specify_doc_dir(user_role.user_id, user_role.role_id)

        # 接收头像
        head_portrait_path = \
            (f"aaa_file/headportrait/" + str(user_id) + str(user_role.role_id) +
             str(head_portrait.filename))
        head_portrait.save(dst=head_portrait_path)
        db_head_portrait = module.HeadPortrait(
            path=head_portrait_path
        )
        extentions.DATABASE.session.add(db_head_portrait)
        extentions.DATABASE.session.commit()
        extentions.DATABASE.session.flush()
        user_role.head_portrait_id = db_head_portrait.head_portrait_id
        extentions.DATABASE.session.commit()
        extentions.DATABASE.session.flush()
        # 接收文件
        for file in files:
            path = f"{doc_dir}/{file.filename}"
            file.save(dst=path)
        # 创建角色
        response_code = VIPUser.create_user_role(
            user_id,
            user_role.role_id,
            user_role.module_name,
            user_role.prompt)
        # 删除服务器上的文档存储
        VIPUser.clean_doc_dir(user_role.user_id, user_role.role_id)
        if response_code == "200":
            # 返回给前端
            return flask.jsonify({
                "code": "200",
                "response": f"角色id为{user_role.role_id}"
            })
        else:
            print("角色创建失败，删除数据库内容！")
            # 删除数据库中创建的对象
            extentions.DATABASE.session.delete(user_role)
            extentions.DATABASE.session.commit()
            # 返回给前端
            return flask.jsonify({
                "code": "400",
                "response": "角色创建失败"
            })
    except Exception as error:
        print("角色创建出现异常！\n", error)
        error_log = module.ErrorLog(
            error_id=2
        )
        extentions.DATABASE.session.add(error_log)
        extentions.DATABASE.session.commit()
        print("角色创建失败，删除数据库内容！")
        # 删除数据库中创建的对象
        extentions.DATABASE.session.delete(user_role)
        extentions.DATABASE.session.commit()
        return flask.jsonify({
            "code": "400",
            "response": "角色创建失败"
        })


@VIP_USER_BP.route("/delete_user_role", methods=['GET', 'POST'])
@flask_login.login_required
def delete_user_role():
    """
    视图函数-删除用户自定义角色
    code对应的含义:
    200: 成功
    400: 失败
    401: 数据库中未找到该角色id
    :return:
    """
    front_datas = flask.request.get_json()
    role_id = front_datas.get("role_id")
    print("role_id", role_id)
    response_code = VIPUser.delete_user_role(role_id)
    if response_code == "200":
        return flask.jsonify({
            "code": "200",
            "response": f"删除角色id为{role_id}"
        })
    elif response_code == "400":
        return flask.jsonify({
            "code": "400",
            "response": "删除角色失败!"
        })
    elif response_code == "401":
        return flask.jsonify({
            "code": "401",
            "response": "数据库中未找到该角色id!"
        })


@VIP_USER_BP.route("/collect_role", methods=['POST'])
@flask_login.login_required
def collect_role():
    """
    收藏角色视图
    Returns:code
    200 表示成功
    400 表示失败

    """
    role_id = flask.request.get_json().get("role_id")
    code = "400"
    if role_id:
        code = VIPUser.set_collect(role_id, True)
    return flask.jsonify(code=code)


@VIP_USER_BP.route("/cancel_collect", methods=['POST'])
@flask_login.login_required
def cancel_collect():
    """
    撤销收藏角色视图
    Returns:code
    200 表示成功
    400 表示失败

    """
    role_id = flask.request.get_json().get("role_id")
    code = "400"
    if role_id:
        code = VIPUser.set_collect(role_id, False)
    return flask.jsonify(code=code)


@VIP_USER_BP.route("/get_roles", methods=['GET'])
@flask_login.login_required
def get_roles():
    """
    获取所有的角色
    Returns:code 200 表示成功 400 表示失败
    列表，其中包含了多个角色信息的字典对象
    """
    user_id = flask.request.args.get("user_id")
    print(user_id)
    code = "400"
    list_roles = []
    head_portrait_id = None
    nickname = None
    if user_id:
        list_roles = VIPUser.get_all_roles(user_id)
        user = module.User.query.get(user_id)
        if user:
            head_portrait_id = user.head_portrait_id
            nickname = user.nickname
            code = "200"
    return flask.jsonify(code=code, data=list_roles,
                         nickname=nickname, head_portrait_id=head_portrait_id)


@VIP_USER_BP.route("/get_role_head_portrait", methods=['GET'])
@flask_login.login_required
def get_head_portrait():
    """
    获取角色头像的视图
    Returns:角色的头像图片文件
    失败的话返回code 400

    """
    head_portrait_id = flask.request.args.get("head_portrait_id")
    if head_portrait_id:
        head_portrait = module.HeadPortrait.query.get(head_portrait_id)
        path = head_portrait.path
        if os.path.isfile(path):
            return flask.send_file(path)
    return flask.jsonify(code="400")


@VIP_USER_BP.route("/get_role_information", methods=['GET'])
@flask_login.login_required
def get_information():
    """
    获取指定角色信息
    Returns:code， data字典
    code 200表示成功
         400表示失败
    data 获取成功则包含角色的相关信息
    {
      "role_name": 角色名称,
      "head_portrait_id": 角色头像id,
      "description": 角色描述,
      "divergency": 角色的发散程度,
      "module_name": 角色使用模型的名称,
      "prompt": 角色的提示词
    }

    """
    role_id = flask.request.args.get("role_id")
    is_built_in = flask.request.args.get("is_built_in", type=str)
    data = {}
    code = "400"
    print(is_built_in,type(is_built_in))
    if role_id and is_built_in:
        if is_built_in == "true":
            role = module.BuiltInRole.query.get(role_id)
            if role:
                data = {
                    "role_name": role.role_name,
                    "head_portrait_id": role.head_portrait_id,
                    "description": role.description,
                    "divergency": role.divergency,
                    "module_name": role.module_name,
                    "prompt": role.prompt
                }
                code = "200"
        elif is_built_in == "false":
            role = module.UserRole.query.get(role_id)
            if role:
                data = {
                    "role_name": role.role_name,
                    "head_portrait_id": role.head_portrait_id,
                    "description": role.description,
                    "divergency": role.divergency,
                    "module_name": role.module_name,
                    "prompt": role.prompt
                }
                code = "200"
    return flask.jsonify(code=code, data=data)


class VIPUser(object):
    """
    vip用户
    """

    @staticmethod
    def specify_doc_dir(user_id, role_id):
        """
        指定文件夹存储路径
        Args:
            user_id:
            role_id:

        Returns:

        """
        # 指定文件夹路径
        doc_dir = os.path.abspath("aaa_file") + "\\roles_db"
        doc_dir = doc_dir.replace('\\', '/')
        doc_dir = f"{doc_dir}/{user_id}"
        doc_dir = doc_dir + f"/{str(role_id)}/doc_dir"
        if not os.path.exists(doc_dir):
            os.makedirs(doc_dir)
        return doc_dir

    @staticmethod
    def clean_doc_dir(user_id, role_id):
        """
        删除服务器上的文件存储
        Args:
            user_id:
            role_id:

        Returns:

        """
        doc_dir = VIPUser.specify_doc_dir(user_id, role_id)
        # 删除服务器上的文档存储
        file_list = os.listdir(doc_dir)
        for file in file_list:
            file_path = os.path.join(doc_dir, file)
            if os.path.isfile(file_path):
                os.remove(file_path)

    @staticmethod
    def create_user_role(user_id, role_id, llm, prompt):
        """
        创建用户自定义角色
        Args:
            user_id:
            role_id:
            llm:
            prompt:

        Returns:

        """
        server_url = "https://23w5971n67.goho.co/create_role"
        # 指定文件夹路径
        doc_dir = VIPUser.specify_doc_dir(user_id, role_id)

        files_to_send = []
        additional_info = {
            "user_id": str(user_id),
            "role_id": str(role_id),
            "llm": str(llm),
            "prompt": str(prompt)
        }
        # 遍历文件夹下的所有文件
        for filename in os.listdir(doc_dir):
            file_path = os.path.join(doc_dir, filename)
            if os.path.isfile(file_path):  # 确保是文件而不是文件夹
                files_to_send.append(("files", open(file_path, "rb")))
        # 发送请求，包含多个文件
        response = requests.post(server_url, files=files_to_send,
                                 data=additional_info)
        response_code = response.json().get("code")
        return response_code

    @staticmethod
    def delete_user_role(role_id):
        """
        删除角色
        Args:
            role_id:

        Returns:

        """
        user_role = module.UserRole.query.get(role_id)
        if user_role:
            server_url = "https://23w5971n67.goho.co/delete_role"
            additional_info = {
                "user_id": str(user_role.user_id),
                "role_id": str(user_role.role_id)
            }
            # 发送请求
            response = requests.post(server_url, json=additional_info)
            response_code = response.json().get("code")
            if response_code == "200":
                try:
                    # 删除数据库中创建的对象
                    extentions.DATABASE.session.delete(user_role)
                    extentions.DATABASE.session.commit()
                    # 删除角色头像
                    # 获取原来头像的信息
                    old_head_portrait_id = user_role.head_portrait_id
                    old_head_portrait = module.HeadPortrait.query.get(
                        old_head_portrait_id)
                    old_path = old_head_portrait.path
                    # 删除原来头像的记录以及图片
                    if old_head_portrait_id != 1 and os.path.exists(old_path):
                        print("旧头像删除成功！")
                        os.remove(old_path)
                        extentions.DATABASE.session.delete(old_head_portrait)
                    extentions.DATABASE.session.commit()
                    return "200"
                except Exception as error:
                    print("删除角色出现异常！\n", error)
                    error_log = module.ErrorLog(
                        error_id=2
                    )
                    extentions.DATABASE.session.add(error_log)
                    extentions.DATABASE.session.commit()
                    return "400"
            else:
                return "400"
        else:
            print("数据库中未找到该角色id!")
            return "401"

    @staticmethod
    def set_collect(role_id, state):
        """
        设置角色的收藏状态
        Args:
            role_id: 角色的编号
            state: 角色的收藏状态

        Returns:code
        200 表示成功
        400 表示失败
        """
        code = "400"
        if role_id:
            role = module.UserRole.query.get(role_id)
            if role:
                role.is_collect = state
                extentions.DATABASE.session.commit()
                code = "200"
        return code

    @staticmethod
    def get_all_roles(user_id):
        """
        获取所有的角色
        Args:
            user_id: vip用户的编号

        Returns:列表
        列表中包含了多个角色的字典对象

        """
        built_in_roles = module.BuiltInRole.query.all()
        user_roles = module.UserRole.query.filter_by(user_id=user_id)
        data = []
        for role in built_in_roles:
            dict_role = {
                "role_id": role.role_id,
                "role_name": role.role_name,
                "head_portrait_id": role.head_portrait_id,
                "is_built_in": True,
                "is_collect": False
            }
            data.append(dict_role)
        for role in user_roles:
            dict_role = {
                "role_id": role.role_id,
                "role_name": role.role_name,
                "head_portrait_id": role.head_portrait_id,
                "is_built_in": False,
                "is_collect": role.is_collect
            }
            data.append(dict_role)
        return data
