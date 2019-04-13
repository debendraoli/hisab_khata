from flask import render_template, request, jsonify
from extensions import db
from flask_login import login_required, current_user
from ..inventory.models import Item
from ..sale.models import Invoice, profit_calculator, InvoicedItem
from . import report


@report.route('/inventory/', methods=['GET', 'POST'])
@login_required
def inventory():
    if request.method == 'POST':
        draw = int(request.form['draw'])
        start = int(request.form['start'])
        length = int(request.form['length'])
        search = request.form['search[value]']
        context = Item.query.filter(Item.company_id == current_user.company_id) \
            .order_by()
        if search[:5] == 'code:':
            context = Item.query.filter(Item.company_id == current_user.company_id) \
                .filter(Item.id.like(search[5:].strip())) \
                .order_by()
        elif search:
            context = Item.query.filter(Item.company_id == current_user.company_id) \
                    .filter(Item.name.like(search)) \
                    .order_by()
        items = {
            'draw': draw,
            'recordsTotal': context.count(),
            'recordsFiltered': context.count(),
            'data': []
            }
        for item_1 in context.offset(start).limit(length).all():
            try:
                sold = int(db.session.query(db.func.sum(InvoicedItem.quantity))
                           .filter(InvoicedItem.item_id == item_1.id).scalar())
            except AttributeError and TypeError:
                sold = 0
            items['data'].append({
                'id': item_1.id,
                'code': item_1.code,
                'name': item_1.name,
                'cost_price': item_1.cost_price,
                'quantity': item_1.quantity,
                'sold': sold,
                'stock': item_1.quantity - sold,
                'stock_value': item_1.quantity * item_1.cost_price,
                'profit_value': item_1.quantity * (item_1.retail_price - item_1.cost_price),
                })
        return jsonify(items)
    data = {
        'total_value_of_stock': db.session.query(db.func.sum(Item.cost_price) * db.func.sum(Item.quantity)).filter(
            Item.company_id == current_user.company_id, Item.quantity != Item.sold).scalar(),
        'stock_total': db.session.query(db.func.count(Item.id)).filter(Item.company_id == current_user.
                                                                       company_id).scalar(),
        'total_profit': profit_calculator(Invoice.query.filter(Invoice.company_id == current_user.company_id).all()),
        'profit_on_hand': db.session.query(db.func.sum(
            Item.retail_price * Item.quantity) - db.func.sum(Item.cost_price * Item.quantity)).filter(
            Item.company_id == current_user.company_id).scalar(),
    }
    return render_template('report/inventory.html', data=data)


@report.route('/expense')
def expense():
    # todo
    return render_template('')


@report.route('/purchase')
def purchase():
    # todo
    return render_template('')


@report.route('/sales')
def sales():
    # todo
    return render_template('')


@report.route('/income')
def income():
    # todo
    return render_template('')


@report.route('/income_vs_expense')
def income_vs_expense():
    # todo
    return render_template('')
