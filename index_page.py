from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from sqlalchemy import or_, func
from models import House, User

index_page = Blueprint('index_page', __name__, template_folder='templates')


@index_page.route('/')
def index():
    """首页"""
    # 查询浏览量最高的8个房源作为热点推荐
    hot_houses = House.query.order_by(House.page_views.desc()).limit(8).all()
    # 查询最新发布的6个房源
    new_houses = House.query.order_by(House.publish_time.desc()).limit(6).all()

    # 获取登录用户信息
    user_name = session.get('user_name')
    user = User.query.filter_by(name=user_name).first() if user_name else None

    return render_template(
        'index.html',
        hot_houses=hot_houses,
        new_houses=new_houses,
        user=user
    )


@index_page.route('/search/keyword/', methods=['POST'])
def search_keyword():
    """智能搜索关键词提示 (AJAX)"""
    keyword = request.form.get('kw', '')
    info_type = request.form.get('info', '')

    if not keyword:
        return jsonify(code=0, info='关键词为空')

    results = []
    if '地区' in info_type:
        # 搜索区域、商圈、小区
        houses = House.query.with_entities(House.region, House.block, House.address, func.count('*')).filter(or_(
            House.region.like(f'%{keyword}%'),
            House.block.like(f'%{keyword}%'),
            House.address.like(f'%{keyword}%')
        )).group_by(House.region, House.block, House.address).limit(9).all()

        results = [{'t_name': f"{h.address}", 'num': h[3]} for h in houses]

    elif '户型' in info_type:
        # 搜索户型
        houses = House.query.with_entities(House.rooms, func.count('*')).filter(
            House.rooms.like(f'%{keyword}%')).group_by(House.rooms).limit(9).all()
        results = [{'t_name': h.rooms, 'num': h[1]} for h in houses]

    if not results:
        return jsonify(code=0, info=f'未找到关于{keyword}的房屋信息！')

    return jsonify(code=1, info=results)

@index_page.route('/query')
def query():
    """处理搜索请求并跳转到搜索结果列表"""
    addr = request.args.get('addr')
    rooms = request.args.get('rooms')

    return redirect(url_for('list_page.search_result', page=1, addr=addr, rooms=rooms))