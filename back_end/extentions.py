#!/usr/bin/env python3.10.13
"""这是一个扩展的文件
包括socket，数据库，邮箱，migration

Copyright 2023 Yan Wang.
License(GPL)
Author: Yan Wang
"""
from flask_sqlalchemy import extension
import flask_migrate
import flask_mail
import flask_login

MAIL = flask_mail.Mail()
DATABASE = extension.SQLAlchemy()
MIGRATE = flask_migrate.Migrate()
LOGIN_MANGER = flask_login.LoginManager()
