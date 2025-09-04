# user_page.py

from flask import Blueprint, render_template, session, redirect, url_for
from models import User, House

# 1. 将蓝图的内部名称改为 'user_page'，函数名改为 show_user_page
user_page = Blueprint('user_page', __name__, template_folder='templates')

# 2. 使用更简洁的URL，并从 app.py 中移入完整的逻辑
@user_page.route('/user/<username>')
def show_user_page(username):
    """用户个人主页"""
    if 'user_name' not in session or session['user_name'] != username:
        # 注意：这里的 'index_page.index' 必须是正确的首页端点名
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