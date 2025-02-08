# -*- coding: utf-8 -*-
# @Time    : 2025/2/3 01:12
# @Author  : HeLong
# @FileName: run.py
# @Software: PyCharm
# @Blog    : https://helong.online/

from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)