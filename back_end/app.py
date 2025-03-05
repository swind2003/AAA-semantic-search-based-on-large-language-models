#!/usr/bin/env python3.10.13
"""这是一个主应用文件
在该文件中完成蓝图注册，以及数据库、邮箱等的配置初始化

Copyright 2023 Yan Wang.
License(GPL)
Author: Yan Wang
"""
from flask import app
import flask_cors

from blue_prints import (
    login_system, semantic_search,
    common_user, administrator,
    vip_user, builtin_role_administrator)
import config
import extentions
import module

APP = app.Flask(__name__)
# # 配置app的config
APP.config.from_object(config)
# 配置其他所需扩展
extentions.DATABASE.init_app(APP)
extentions.MIGRATE.init_app(app=APP, db=extentions.DATABASE)
extentions.MAIL.init_app(app=APP)
extentions.LOGIN_MANGER.init_app(app=APP)
# 跨域访问配置
flask_cors.CORS(app=APP, supports_credentials=True, origins='*',
                methods=['GET', 'POST', 'DELETE'],
                allow_headers='*')

# 登录蓝图注册
APP.register_blueprint(login_system.LOGIN_BP)
# 语义搜索蓝图注册
APP.register_blueprint(semantic_search.SEMANTIC_SEARCH_BP)
# 用户蓝图注册
APP.register_blueprint(common_user.USER_BLUE_PRINT)
# 管理员蓝图注册
APP.register_blueprint(administrator.ADMINISTRATOR_BP)
# vip用户蓝图注册
APP.register_blueprint(vip_user.VIP_USER_BP)
# 内置管理员蓝图注册
APP.register_blueprint(builtin_role_administrator.BUILTIN_ROLE_ADMINISTRATOR_BP)


# 注册flask-login的一个回调函数
@extentions.LOGIN_MANGER.user_loader
def loader_user(user_id):
    return module.User.query.get(user_id)


if __name__ == '__main__':
    APP.run(host='0.0.0.0', port=5000)
