from flask import request, session, redirect, url_for, jsonify, render_template
from sqlalchemy import or_

from settings import app, db
from models import House, User, Recommend
import math
from index_page import index_page
from search_list import search_list_page
from list_page import list_page
from detail_page import detail_page
from user_page import user_page
app.register_blueprint(user_page, url_prefix='/')
app.register_blueprint(detail_page, url_prefix='/')
app.register_blueprint(list_page, url_prefix='/')
#  修改蓝图前缀避免冲突
app.register_blueprint(search_list_page,url_prefix='/search')
app.register_blueprint(index_page,url_prefix='/')
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
@app.route('/list/<string:category>/<int:page>')
def house_list(category, page):
    """
    房源列表页
    :param category: 类别 (pattern: 默认模式, hot_house: 热点房源)
    :param page: 页码
    """
    per_page = 10  # 每页显示10条数据

    if category == 'pattern':
        # 按发布时间降序排序
        pagination = House.query.order_by(House.publish_time.desc()).paginate(page=page, per_page=per_page, error_out=False)
    elif category == 'hot_house':
        # 按浏览量降序排序
        pagination = House.query.order_by(House.page_views.desc()).paginate(page=page, per_page=per_page, error_out=False)
    else:
        # 默认排序
        pagination = House.query.paginate(page=page, per_page=per_page, error_out=False)

    houses = pagination.items

    user_name = session.get('user_name')
    user = User.query.filter_by(name=user_name).first() if user_name else None

    return render_template('list.html', houses=houses, pagination=pagination, user=user, category=category)


# --- 搜索功能 ---

@app.route('/query')
def query():
    """处理搜索请求并跳转到搜索结果列表"""
    addr = request.args.get('addr')
    rooms = request.args.get('rooms')

    # 将搜索条件存入session，以便结果页使用
    session['search_addr'] = addr
    session['search_rooms'] = rooms

    return redirect(url_for('search_result', page=1))


@app.route('/search_result/<int:page>')
def search_result(page):
    """显示搜索结果"""
    per_page = 10
    addr = session.get('search_addr')
    rooms = session.get('search_rooms')

    query_obj = House.query
    if addr:
        # 支持区域、商圈、小区的模糊搜索
        query_obj = query_obj.filter(or_(
            House.region.like(f"%{addr}%"),
            House.block.like(f"%{addr}%"),
            House.address.like(f"%{addr}%")
        ))
    if rooms:
        query_obj = query_obj.filter(House.rooms.like(f"%{rooms}%"))

    pagination = query_obj.order_by(House.publish_time.desc()).paginate(page=page, per_page=per_page, error_out=False)
    houses = pagination.items

    user_name = session.get('user_name')
    user = User.query.filter_by(name=user_name).first() if user_name else None

    # 使用 list.html 渲染搜索结果
    return render_template('list.html', houses=houses, pagination=pagination, user=user, query_str=addr or rooms, query_type='搜索结果')

if __name__ == '__main__':
    app.run(debug=True)