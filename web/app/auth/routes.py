# -*- coding: utf-8 -*-
# @Time    : 2025/2/3 11:11
# @Author  : HeLong
# @FileName: routes.py
# @Software: PyCharm
# @Blog    : https://helong.online/

from flask import Blueprint, render_template, redirect, url_for, flash
from app.auth.forms import RegistrationForm, LoginForm
from app.models import User
from app import db
from flask_login import login_user, logout_user

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('注册成功！请登录', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for('main.index'))  # 假设后续有主页路由
        else:
            flash('用户名或密码错误', 'danger')
    return render_template('auth/login.html', form=form)

@auth_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))