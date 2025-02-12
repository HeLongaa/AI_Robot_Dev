# -*- coding: utf-8 -*-
# @Time    : 2025/2/12 22:44
# @Author  : HeLong
# @FileName: run.py
# @Software: PyCharm
# @Blog    : https://helong.online/

from flask import Flask, render_template
app = Flask(__name__)


app.register_blueprint(auth, url_prefix='/auth')
app.register_blueprint(manager, url_prefix='/manager')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/docx')
def docx():
    return render_template('docx.html')

@app.route('/demo')
def demo():
    return render_template('demo.html')

@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True)
