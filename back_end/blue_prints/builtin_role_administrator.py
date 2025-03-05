#!/usr/bin/env python3.10.13
"""对前端页面提供的内置角色管理者api.

Copyright 2023 Li Jinhua.
License(GPL)
Author: Li Jinhua
"""
import os

import flask_login
import requests
import flask

import extentions
import instrument
import module

# /builtin_role_administrator
BUILTIN_ROLE_ADMINISTRATOR_BP = flask.Blueprint(
    "builtin_role_administrator",
    __name__,
    url_prefix="/builtin_role_administrator")


@BUILTIN_ROLE_ADMINISTRATOR_BP.route(
    "/information/get_openai_api_key", methods=['GET', 'POST'])
@flask_login.login_required
def get_openai_api_key():
    """
    视图函数-前端获取openai的api密钥
    code对应的含义:
    200: 成功
    400: 失败
    Returns:

    """
    print("前端获取openai的api密钥")
    try:
        openai_api_key = BuiltinRoleAdministrator.get_openai_api_key()
        return flask.jsonify({
            "code": "200",
            "openai_api_key": openai_api_key
        })
    except Exception as error:
        print("获取openai的api密钥出现问题\n", error)
        error_log = module.ErrorLog(
            error_id=3
        )
        extentions.DATABASE.session.add(error_log)
        extentions.DATABASE.session.commit()
        return flask.jsonify({
            "code": "400",
            "openai_api_key": ""
        })


@BUILTIN_ROLE_ADMINISTRATOR_BP.route(
    "/information/write_openai_api_key", methods=['GET', 'POST'])
@flask_login.login_required
def write_openai_api_key():
    """
    视图函数-将openai的api密钥写入文档
    code对应的含义:
    200: 成功
    400: 失败
    :return:
    """
    openai_api_key = flask.request.args.get('openai_api_key')
    print("将openai的api密钥写入文档")
    try:
        BuiltinRoleAdministrator.write_openai_api_key(openai_api_key)
        return flask.jsonify({
            "code": "200"
        })
    except Exception as error:
        print("写入密钥出现问题\n", error)
        error_log = module.ErrorLog(
            error_id=3
        )
        extentions.DATABASE.session.add(error_log)
        extentions.DATABASE.session.commit()
        return flask.jsonify({
            "code": "400"
        })


@BUILTIN_ROLE_ADMINISTRATOR_BP.route(
    "/information/get_role_information", methods=['GET', 'POST'])
@flask_login.login_required
def get_role_information():
    """
    视图函数-前端获取角色信息
    :return:
    """
    print("前端获取角色信息")
    user_id = flask.request.args.get('user_id')
    response = []
    if user_id == "000000":
        builtin_role_list = module.BuiltInRole.query.all()
        for role in builtin_role_list:
            print("role_id", role.role_id)
            json_data = {
                "role_id": role.role_id,
                "role_name": role.role_name,
                "description": role.description,
                "have_document_store": role.have_document_store
            }
            response.append(json_data)
    return flask.jsonify(data=response)


@BUILTIN_ROLE_ADMINISTRATOR_BP.route(
    "/information/get_role_information_detail", methods=['GET', 'POST'])
@flask_login.login_required
def get_role_information_detail():
    """
    视图函数-前端获取角色详细信息
    code对应的含义:
    200: 成功
    400: 失败
    :return:
    """
    print("前端获取角色详细信息")
    user_id = flask.request.args.get('user_id')
    role_id = flask.request.args.get("role_id")
    if user_id == "000000":
        builtin_role = module.BuiltInRole.query.get(role_id)
        return flask.jsonify({
            "code": "200",
            "role_name": builtin_role.role_name,
            "description": builtin_role.description,
            "divergency": builtin_role.divergency,
            "module_name": builtin_role.module_name,
            "prompt": builtin_role.prompt
        })
    else:
        return flask.jsonify({
            "code": "400",
            "role_name": "",
            "description": "",
            "divergency": "",
            "module_name": "",
            "prompt": ""
        })


@BUILTIN_ROLE_ADMINISTRATOR_BP.route(
    "/information/get_role_head_portrait", methods=['GET', 'POST'])
@flask_login.login_required
def get_role_head_portrait():
    """
    视图函数-前端获取角色头像
    code对应的含义:
    400: 失败
    :return:
    """
    user_id = flask.request.args.get('user_id')
    role_id = flask.request.args.get('role_id')
    print("前端获取角色头像")
    print("user_id", user_id)
    print("role_id", role_id)
    if user_id == "000000":
        role = module.BuiltInRole.query.get(role_id)
        head_portrait = module.HeadPortrait.query.get(role.head_portrait_id)
        if head_portrait:
            path = head_portrait.path
            return flask.send_file(path)
    return flask.jsonify(code="400", message="获取头像出错")


@BUILTIN_ROLE_ADMINISTRATOR_BP.route(
    "/create_builtin_role", methods=['GET', 'POST'])
@flask_login.login_required
def create_builtin_role():
    """
    视图函数-创建内置角色
    code对应的含义:
    200: 成功
    400: 失败
    :return:
    """
    user_id = flask.request.form.get("user_id")
    if user_id == "000000":
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
        # 在数据库中生成内置角色
        built_in_role = module.BuiltInRole(
            role_name=role_name,
            head_portrait_id=None,
            description=description,
            divergency=divergency,
            module_name=module_name,
            module_api=module_api,
            prompt=prompt
        )
        try:
            extentions.DATABASE.session.add(built_in_role)
            extentions.DATABASE.session.commit()
            extentions.DATABASE.session.flush()

            # 指定文件夹路径
            doc_dir = BuiltinRoleAdministrator.specify_doc_dir(
                user_id, str(built_in_role.role_id))

            # 接收头像
            head_portrait_path = \
                (f"aaa_file/headportrait/" + str(user_id) +
                 str(built_in_role.role_id) + str(head_portrait.filename))
            head_portrait.save(dst=head_portrait_path)
            db_head_portrait = module.HeadPortrait(
                path=head_portrait_path
            )
            extentions.DATABASE.session.add(db_head_portrait)
            extentions.DATABASE.session.commit()
            extentions.DATABASE.session.flush()
            built_in_role.head_portrait_id = db_head_portrait.head_portrait_id
            extentions.DATABASE.session.commit()
            extentions.DATABASE.session.flush()
            # 接收文件
            for file in files:
                path = f"{doc_dir}/{file.filename}"
                file.save(dst=path)
            # 创建角色
            response_code = BuiltinRoleAdministrator.create_builtin_role(
                user_id,
                built_in_role.role_id,
                built_in_role.module_name,
                built_in_role.prompt)
            # 删除服务器上的文档存储
            BuiltinRoleAdministrator.clean_doc_dir(
                user_id, built_in_role.role_id)
            if response_code == "200":
                # 返回给前端
                return flask.jsonify({
                    "code": "200",
                    "response": f"角色id为{built_in_role.role_id}"
                })
            else:
                print("角色创建失败，删除数据库内容！")
                # 删除数据库中创建的对象
                extentions.DATABASE.session.delete(built_in_role)
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
            extentions.DATABASE.session.delete(built_in_role)
            extentions.DATABASE.session.commit()
            return flask.jsonify({
                "code": "400",
                "response": "角色创建失败"
            })


@BUILTIN_ROLE_ADMINISTRATOR_BP.route(
    "/edit_role_attribute", methods=['GET', 'POST'])
@flask_login.login_required
def edit_role_attribute():
    """
    视图函数-修改内置角色属性
    code对应的含义:
    200: 成功
    400: 失败
    401: 数据库中未找到该角色id
    402: 角色头像修改失败
    403: 角色头像图片格式不符合要求
    Returns:

    """
    print("修改内置角色属性")
    try:
        head_portrait = flask.request.files.get('head_portrait')
        user_id = flask.request.form.get('user_id')
        role_id = flask.request.form.get('role_id')
        role_name = flask.request.form.get('role_name')
        description = flask.request.form.get('description')
        prompt = flask.request.form.get('prompt')
        print("role_id", role_id)
        attribute_code = BuiltinRoleAdministrator.edit_role_attribute(
            role_id, role_name, description, prompt
        )
        if head_portrait:
            print("接收到头像图片")
            if instrument.determine_suffix(head_portrait.filename):
                head_portrait_path = \
                    (f"aaa_file/headportrait/" + str(user_id) +
                     str(role_id) + str(head_portrait.filename))
                head_success = BuiltinRoleAdministrator.change_role_head_portrait(
                    role_id, head_portrait_path)
                head_portrait.save(dst=head_portrait_path)
                print("存储图片到路径:\n", head_portrait_path)
                if head_success and attribute_code == "200":
                    return flask.jsonify({
                        "code": "200",
                        "response": "角色属性修改成功！"
                    })
                elif not head_success:
                    return flask.jsonify({
                        "code": "402",
                        "response": "角色头像修改失败！"
                    })
                elif attribute_code == "400":
                    return flask.jsonify({
                        "code": "400",
                        "response": "角色属性修改失败！"
                    })
                elif attribute_code == "401":
                    return flask.jsonify({
                        "code": "401",
                        "response": "数据库中未找到该角色id!"
                    })
            else:
                return flask.jsonify({
                    "code": "403",
                    "response": "角色头像图片格式不符合要求"
                })
        else:
            if attribute_code == "200":
                return flask.jsonify({
                    "code": "200",
                    "response": "角色属性修改成功！"
                })
            elif attribute_code == "400":
                return flask.jsonify({
                    "code": "400",
                    "response": "角色属性修改失败！"
                })
            elif attribute_code == "401":
                return flask.jsonify({
                    "code": "401",
                    "response": "数据库中未找到该角色id!"
                })
    except Exception as error:
        print("修改内置角色出现异常！\n", error)
        error_log = module.ErrorLog(
            error_id=2
        )
        extentions.DATABASE.session.add(error_log)
        extentions.DATABASE.session.commit()
        return flask.jsonify({
            "code": "400",
            "response": "角色属性修改失败！"
        })


@BUILTIN_ROLE_ADMINISTRATOR_BP.route(
    "/add_role_store", methods=['GET', 'POST'])
@flask_login.login_required
def add_builtin_role_store():
    """
    视图函数-给内置角色向量数据库添加文档
    code对应的含义:
    200: 成功
    400: 失败
    401: 数据库中未找到该角色
    Returns:

    """
    role_id = flask.request.form.get("role_id")
    files = flask.request.files.getlist("files")
    built_in_role = module.BuiltInRole.query.get(role_id)
    try:
        # 指定文件夹路径
        doc_dir = BuiltinRoleAdministrator.specify_doc_dir(
            "000000", role_id)
        # 接收文件
        for file in files:
            path = f"{doc_dir}/{file.filename}"
            file.save(dst=path)
        # 将文件添加到api主机
        response_code = BuiltinRoleAdministrator.add_builtin_role_store(
            user_id="000000",
            role_id=built_in_role.role_id,
            llm=built_in_role.module_name,
            prompt=built_in_role.prompt,
        )
        # 删除服务器上的文档存储
        BuiltinRoleAdministrator.clean_doc_dir("000000", role_id)

        if response_code == "200":
            # 返回给前端
            return flask.jsonify({
                "code": "200",
                "response": f"角色id为{role_id}"
            })
        elif response_code == "400":
            # 返回给前端
            return flask.jsonify({
                "code": "400",
                "response": "添加文档失败"
            })
        elif response_code == "401":
            return flask.jsonify({
                "code": "401",
                "response": "数据库中未找到该角色id!"
            })
    except Exception as error:
        print("添加文档出现异常！\n", error)
        error_log = module.ErrorLog(
            error_id=3
        )
        extentions.DATABASE.session.add(error_log)
        extentions.DATABASE.session.commit()
        return flask.jsonify({
            "code": "400",
            "response": "添加文档失败"
        })


class BuiltinRoleAdministrator(object):
    """
    内置角色管理者
    """

    @staticmethod
    def get_openai_api_key():
        """
        获得api密钥
        Returns:

        """
        # 指定文件夹路径
        folder_path = os.path.abspath("aaa_file") + "\\openai_api_key"
        # folder_path = \
        #     ("E:\\CodeFile\\multilingual_project\\test\\"
        #      "chataaa\\aaa_file\\openai_api_key")
        folder_path = folder_path.replace('\\', '/')
        file_path = f"{folder_path}/openai_api_key.txt"
        # file_path = file_path.replace('/', '\\')
        # print(file_path)
        with open(file_path, 'r', encoding='utf-8') as file:
            openai_api_key = file.read()
        # print(openai_api_key)
        return openai_api_key

    @staticmethod
    def write_openai_api_key(openai_api_key):
        """
        将api密钥写入文档
        Args:
            openai_api_key:

        Returns:

        """
        # 指定文件夹路径
        folder_path = os.path.abspath("aaa_file") + "\\openai_api_key"
        folder_path = folder_path.replace('\\', '/')
        file_path = f"{folder_path}/openai_api_key.txt"
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(openai_api_key)

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
        doc_dir = BuiltinRoleAdministrator.specify_doc_dir(user_id, role_id)
        # 删除服务器上的文档存储
        file_list = os.listdir(doc_dir)
        for file in file_list:
            file_path = os.path.join(doc_dir, file)
            if os.path.isfile(file_path):
                os.remove(file_path)

    @staticmethod
    def create_builtin_role(user_id, role_id, llm, prompt):
        """
        创建内置角色
        Args:
            user_id:
            role_id:
            llm:
            prompt:

        Returns:

        """
        server_url = "https://23w5971n67.goho.co/create_role"
        # 指定文件夹路径
        doc_dir = BuiltinRoleAdministrator.specify_doc_dir(user_id, role_id)

        files_to_send = []
        additional_info = {
            "user_id": user_id,
            "role_id": role_id,
            "llm": llm,
            "prompt": prompt
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
    def change_role_head_portrait(role_id, file_path):
        """
        修改角色头像函数
        Args:
            role_id: 用户编号
            file_path: 头像保存的路径

        Returns:布尔值
        True 表示修改成功
        False 表示修改失败

        """
        role = module.BuiltInRole.query.get(role_id)
        if role:
            # 获取原来头像的信息
            old_head_portrait_id = role.head_portrait_id
            old_head_portrait = module.HeadPortrait.query.get(
                old_head_portrait_id)
            old_path = old_head_portrait.path
            # 创建新头像
            head_portrait = module.HeadPortrait(path=file_path)
            extentions.DATABASE.session.add(head_portrait)
            extentions.DATABASE.session.commit()
            extentions.DATABASE.session.flush()
            role.head_portrait_id = head_portrait.head_portrait_id
            # 删除原来头像的记录以及图片
            if old_head_portrait_id != 1 and os.path.exists(old_path):
                os.remove(old_path)
                extentions.DATABASE.session.delete(old_head_portrait)
                print("旧头像删除成功！")
            extentions.DATABASE.session.commit()
            return True
        return False

    @staticmethod
    def edit_role_attribute(role_id, role_name, description, prompt):
        """
        修改内置角色属性
        Args:
            role_id:
            role_name:
            description:
            prompt:

        Returns:

        """
        try:
            role = module.BuiltInRole.query.get(role_id)
            if role:
                role.role_name = role_name
                role.description = description
                role.prompt = prompt
                extentions.DATABASE.session.commit()
            else:
                print("数据库中未找到该角色id!")
                return "401"
        except Exception as error:
            print("角色修改出现异常！\n", error)
            return "400"
        return "200"

    @staticmethod
    def add_builtin_role_store(user_id, role_id, llm, prompt):
        """
`       给内置角色向量数据库添加文档
        Args:
            user_id:
            role_id:
            llm:
            prompt:

        Returns:

        """
        role = module.BuiltInRole.query.get(role_id)
        if role:
            server_url = "https://23w5971n67.goho.co/add_files"
            # 指定文件夹路径
            doc_dir = BuiltinRoleAdministrator.specify_doc_dir(user_id, role_id)
            files_to_send = []
            additional_info = {
                "user_id": user_id,
                "role_id": role_id,
                "llm": llm,
                "prompt": prompt
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
        else:
            print("数据库中未找到该角色id!")
            return "401"
