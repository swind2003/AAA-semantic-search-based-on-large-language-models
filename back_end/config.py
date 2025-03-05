#!/usr/bin/env python3.10.13
"""这是app的配置文件

Copyright 2023 Yan Wang.
License(GPL)
Author: Yan Wang
"""
# 主机名
HOST = "*"
# 端口号
PORT = 3306
# 登录MySQL的用户名
USERNAME = "*"
# 密码
PASSWORD = "*"
# 数据库的名称
DATABASE = "*"
DB_URI = 'mysql+pymysql://{}:{}@{}:{}/{}?charset=utf8mb4'.format(USERNAME,
                                                                 PASSWORD, HOST,
                                                                 PORT, DATABASE)

SQLALCHEMY_DATABASE_URI = DB_URI

# 邮箱配置
MAIL_SERVER = "*"
MAIL_USE_SSL = True
MAIL_PORT = 465
MAIL_USERNAME = "*"
MAIL_PASSWORD = "*"
MAIL_DEFAULT_SENDER = "*", "*"

# socketio配置
SECRET_KEY = '*'

# cookie设置
SESSION_COOKIE_SAMESITE = None
