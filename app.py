# app.py

from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    redirect,
    url_for,
    session,
)
from settings import app, db
from index_page import index_page
from list_page import list_page
from detail_page import detail_page
from models import House, User, Recommend

app.register_blueprint(index_page, url_prefix='/')
app.register_blueprint(list_page, url_prefix='/')
app.register_blueprint(detail_page, url_prefix='/')

# 用户登录、注册、登出路由
# 为了保持用户登录状态的统一管理，将这些路由放在主应用中
@app.route('/login', methods=['POST'])
def login():
    """用户登录"""
    username = request.form.get('username')
    password = request.form.get('password')

    user = User.query.filter_by(name=username, password=password).first()

    if user:
        session['user_id'] = user.id
        session['user_name'] = user.name
        return redirect(url_for('index_page.index'))
    else:
        # 实际项目中应返回错误提示
        return redirect(url_for('index_page.index'))


@app.route('/register', methods=['POST'])
def register():
    """用户注册"""
    username = request.form.get('username')
    password = request.form.get('password')
    email = request.form.get('email')

    # 检查用户名是否已存在
    if User.query.filter_by(name=username).first():
        # 用户名已存在，应返回错误提示
        return redirect(url_for('index_page.index'))

    new_user = User(name=username, password=password, email=email)
    db.session.add(new_user)
    db.session.commit()

    # 注册成功后自动登录
    session['user_id'] = new_user.id
    session['user_name'] = new_user.name

    return redirect(url_for('index_page.index'))


@app.route('/logout')
def logout():
    """用户登出"""
    session.clear()
    return jsonify(valid='1', msg='已退出登录')


if __name__ == '__main__':
    app.run(debug=True)