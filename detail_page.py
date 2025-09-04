from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from models import House, User, Recommend, db

detail_page = Blueprint('detail_page', __name__, template_folder='templates')


@detail_page.route('/house/<int:house_id>')
def house_detail(house_id):
    """房源详情页"""
    house = House.query.get_or_404(house_id)

    # 增加浏览量
    house.page_views = (house.page_views or 0) + 1
    db.session.commit()

    # 根据当前房源的小区推荐相似房源
    recommendations = House.query.filter(
        House.address == house.address,
        House.id != house.id
    ).limit(6).all()

    user_name = session.get('user_name')
    user = User.query.filter_by(name=user_name).first() if user_name else None

    if user:
        # 记录用户浏览历史
        seen_ids = user.seen_id.split(',') if user.seen_id else []
        if str(house_id) not in seen_ids:
            seen_ids.append(str(house_id))
            user.seen_id = ','.join(seen_ids)
            db.session.commit()

    return render_template('detail_page.html', house=house, recommendations=recommendations, user=user)


@detail_page.route('/user/<string:username>')
def user_profile(username):
    """用户个人主页"""
    if 'user_name' not in session or session['user_name'] != username:
        return redirect(url_for('index_page.index'))

    user = User.query.filter_by(name=username).first_or_404()

    # 获取收藏的房源
    collected_houses = []
    if user.collect_id:
        collect_ids = [int(i) for i in user.collect_id.split(',') if i]
        collected_houses = House.query.filter(House.id.in_(collect_ids)).all()

    # 获取浏览记录
    seen_houses = []
    if user.seen_id:
        seen_ids = [int(i) for i in user.seen_id.split(',') if i]
        seen_houses = House.query.filter(House.id.in_(seen_ids)).all()

    return render_template('user_page.html', user=user, collected_houses=collected_houses, seen_houses=seen_houses)


@detail_page.route('/add/collection/<int:house_id>')
def add_collection(house_id):
    """添加收藏 (AJAX)"""
    if 'user_id' not in session:
        return jsonify(valid='0', msg='请先登录！')

    user = User.query.get(session['user_id'])

    collect_ids = user.collect_id.split(',') if user.collect_id else []
    if str(house_id) not in collect_ids:
        collect_ids.append(str(house_id))
        user.collect_id = ','.join(filter(None, collect_ids))  # 过滤空字符串
        db.session.commit()
        return jsonify(valid='1', msg='收藏成功！')
    else:
        return jsonify(valid='0', msg='您已收藏过该房源！')


@detail_page.route('/collect_off', methods=['POST'])
def collect_off():
    """取消收藏 (AJAX)"""
    house_id = request.form.get('house_id')
    user_name = request.form.get('user_name')

    if session.get('user_name') != user_name:
        return jsonify(valid='0', msg='用户验证失败！')

    user = User.query.filter_by(name=user_name).first()
    if not user or not user.collect_id:
        return jsonify(valid='0', msg='操作失败！')

    collect_ids = user.collect_id.split(',')
    if house_id in collect_ids:
        collect_ids.remove(house_id)
        user.collect_id = ','.join(collect_ids)
        db.session.commit()
        return jsonify(valid='1', msg='已取消收藏')
    return jsonify(valid='0', msg='未找到该收藏记录')


@detail_page.route('/del_record', methods=['POST'])
def del_record():
    """清空浏览记录 (AJAX)"""
    user_name = request.form.get('user_name')
    if session.get('user_name') != user_name:
        return jsonify(valid='0', msg='用户验证失败！')

    user = User.query.filter_by(name=user_name).first()
    if user:
        user.seen_id = ''
        db.session.commit()
        return jsonify(valid='1', msg='浏览记录已清空')
    return jsonify(valid='0', msg='操作失败')


@detail_page.route('/modify/userinfo/<string:field>', methods=['POST'])
def modify_userinfo(field):
    """修改用户信息 (AJAX)"""
    if 'user_name' not in session:
        return jsonify(ok='0')

    user = User.query.filter_by(name=session['user_name']).first()
    if not user:
        return jsonify(ok='0')

    if field == 'name':
        new_name = request.form.get('name')
        # 检查新用户名是否已存在
        if User.query.filter(User.name == new_name).first():
            return jsonify(ok='0', msg='用户名已存在')
        user.name = new_name
        session['user_name'] = new_name  # 更新session
    elif field == 'addr':
        user.addr = request.form.get('addr')
    elif field == 'pd':
        user.password = request.form.get('pd')
    elif field == 'email':
        user.email = request.form.get('email')
    else:
        return jsonify(ok='0')

    db.session.commit()
    return jsonify(ok='1')


@detail_page.route('/get/scatterdata/<region>')
def get_scatter_data(region):
    # 示例：返回价格和面积的散点图数据
    return jsonify(data=[[10, 8.04], [8, 6.95], [13, 7.58]])


@detail_page.route('/get/piedata/<region>')
def get_pie_data(region):
    # 示例：返回户型占比饼图数据
    return jsonify(data=[
        {'value': 335, 'name': '2室1厅'},
        {'value': 310, 'name': '3室1厅'},
        {'value': 234, 'name': '1室1厅'}
    ])


@detail_page.route('/get/columndata/<region>')
def get_column_data(region):
    # 示例：返回小区房源数量柱状图数据
    return jsonify(data={
        'x_axis': ['小区A', '小区B', '小区C'],
        'y_axis': [120, 200, 150]
    })


@detail_page.route('/get/brokenlinedata/<region>')
def get_broken_line_data(region):
    # 示例：返回户型价格走势折线图数据
    return jsonify(data={
        'legend': ['2室1厅', '3室1厅'],
        'x_axis': ['1月', '2月', '3月'],
        'series': [
            {'name': '2室1厅', 'type': 'line', 'data': [3000, 3200, 3100]},
            {'name': '3室1厅', 'type': 'line', 'data': [4500, 4600, 4800]}
        ]
    })