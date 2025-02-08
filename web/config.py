# -*- coding: utf-8 -*-
# @Time    : 2025/2/3 11:06
# @Author  : HeLong
# @FileName: config.py
# @Software: PyCharm
# @Blog    : https://helong.online/

import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-123'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False