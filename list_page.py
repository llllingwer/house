from flask import Blueprint, render_template, request, session, redirect, url_for
from sqlalchemy import or_
from models import House, User

list_page = Blueprint('list_page', __name__, template_folder='templates')


@list_page.route('/list/<string:category>/<int:page>')
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

    # 传递 category 参数给模板，以便分页链接能正确生成
    return render_template('list.html', houses=houses, pagination=pagination, user=user, category=category)


@list_page.route('/search_result/<int:page>')
def search_result(page):
    """显示搜索结果"""
    per_page = 10
    addr = request.args.get('addr')
    rooms = request.args.get('rooms')

    query = House.query
    if addr:
        query = query.filter(or_(
            House.region.like(f"%{addr}%"),
            House.block.like(f"%{addr}%"),
            House.address.like(f"%{addr}%")
        ))
    if rooms:
        query = query.filter(House.rooms.like(f"%{rooms}%"))

    pagination = query.order_by(House.publish_time.desc()).paginate(page=page, per_page=per_page, error_out=False)
    houses = pagination.items

    user_name = session.get('user_name')
    user = User.query.filter_by(name=user_name).first() if user_name else None

    # 传递查询参数给模板，以便分页链接能正确生成
    return render_template('search_list.html', houses=houses, pagination=pagination, user=user, query_str=addr or rooms, query_type='地区' if addr else '户型')