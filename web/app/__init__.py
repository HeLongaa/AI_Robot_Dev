# -*- coding: utf-8 -*-
# @Time    : 2025/2/3 11:09
# @Author  : HeLong
# @FileName: __init__.py
# @Software: PyCharm
# @Blog    : https://helong.online/

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # 初始化扩展
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'  # 设置登录视图


    from app.auth.routes import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    return app