from flask import Blueprint, render_template, request, redirect, url_for
from models import House

search_list_page = Blueprint('search_page', __name__, template_folder='templates')


@search_list_page.route('/query', methods=['GET'])
def query():
    addr = request.args.get('addr', '', type=str).strip()
    rooms = request.args.get('rooms', '', type=str).strip()

    query_filter = None
    query_str = None
    query_type = None

    if addr:
        query_filter = House.address.contains(addr)
        query_str = addr
        query_type = "地区"
    elif rooms:
        query_filter = House.rooms.contains(rooms)
        query_str = rooms
        query_type = "户型"

    if query_filter is None or not query_str:
        return redirect(url_for('index.index'))

    page = request.args.get('page', 1, type=int)

    try:
        # 【已修复】将 page 参数改为关键字参数 page=page
        paginate = House.query.filter(query_filter).paginate(page=page, per_page=6)
    except Exception:
        page = 1
        # 【已修复】此处也需要修改
        paginate = House.query.filter(query_filter).paginate(page=page, per_page=6)

    return render_template(
        "search_list.html",
        houses=paginate.items,
        paginate=paginate,
        query_str=query_str,
        query_type=query_type
    )