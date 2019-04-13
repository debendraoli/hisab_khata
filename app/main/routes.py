from datetime import timedelta, datetime
from flask import render_template, redirect, url_for, jsonify, request, send_from_directory,\
    current_app as app, abort
from flask_login import login_required, current_user
from extensions import db
from ..auth.models import User
from ..inventory.models import Item, WareHouse
from ..people.models import Supplier, Notification, Customer
from ..sale.models import Invoice, get_sales_by_range, profit_calculator
from ..transaction.models import Payment, PaymentMethod
from . import main
from .models import Purchase, PurchasedItem


@main.route('/')
def index():
    return redirect(url_for('main.dashboard'))


@main.route('/dashboard/')
@login_required
def dashboard():
    today_sold_products = get_sales_by_range(current_user.company_id, current_user.back_to_past(),
                                             current_user.get_local_time())
    monthly_sold_products = get_sales_by_range(current_user.company_id, current_user.get_local_time() - timedelta(days=30),
                                               current_user.get_local_time())
    total_sold_products = Invoice.query.filter(Invoice.company_id == current_user.company_id).all()
    data = {
        'revenue': {
            'today': db.session.query(db.func.sum(Payment.amount)).filter(Payment.company_id == current_user.company_id,
                                                                          Payment.datetime.between(
                                                                           current_user.back_to_past(),
                                                                           current_user.get_local_time())).scalar(),
            'month': db.session.query(db.func.sum(Payment.amount)).filter(Payment.company_id == current_user.company_id,
                                                                          Payment.datetime.between(
                                                                            current_user.get_local_time() - timedelta(days=30),
                                                                            current_user.get_local_time())).scalar(),

            'total': db.session.query(db.func.sum(Payment.amount)).filter(
                Payment.company_id == current_user.company_id).scalar()
        }
        ,
        'profit':
            {
            'today': profit_calculator(today_sold_products),
            'month': profit_calculator(monthly_sold_products),
            'total': profit_calculator(total_sold_products)
            },
        'sales':
            {
            'today': db.session.query(db.func.count(Invoice.id)).filter(
                Invoice.company_id == current_user.company_id,
                Invoice.datetime.between(
                    current_user.back_to_past(),
                    current_user.get_local_time())).scalar(),
            'month': db.session.query(db.func.count(Invoice.id)).filter(
                Invoice.company_id == current_user.company_id,
                Invoice.datetime.between(
                    current_user.get_local_time() - timedelta(days=30), current_user.get_local_time())).scalar(),
            'total': db.session.query(db.func.count(Invoice.id))
                .filter(Invoice.company_id == current_user.company_id).scalar()
            },
        'value_of_stock':
            db.session.query(db.func.sum(Item.cost_price) * db.func.sum(Item.quantity))
            .filter(Item.company_id == current_user.company_id, ).scalar(),

        'people':
            {
                'staff': db.session.query(db.func.count(User.id)).filter_by(company_id=current_user.company_id,
                                                                            status=True).scalar(),
                'supplier': db.session.query(db.func.count(Supplier.id)).filter_by(company_id=current_user.company_id,
                                                                                   status=True).scalar(),

                'customer': db.session.query(db.func.count(Customer.id)).filter_by(
                    company_id=current_user.company_id,
                    status=True).scalar()
           },

        'account_balance': PaymentMethod.query.filter(PaymentMethod.company_id == current_user.company_id,
                                                      PaymentMethod.status).all(),
        'notification': db.session.query(db.func.count(Notification.id)).filter(
            Notification.user_id == current_user.id, Notification.status).scalar()
    }
    return render_template('dashboard.html', title='Dashboard', data=data)


@main.route('/purchase/', methods=['GET', 'POST'])
@login_required
def purchase():
    if request.method == 'POST':
        draw = int(request.form['draw'])
        start = int(request.form['start'])
        length = int(request.form['length'])
        search = request.form['search[value]']
        context = Purchase.query.filter_by(company_id=current_user.company_id)\
            .order_by()
        if search[:5] == 'code:':
            context = context.filter(Purchase.code.like(search[5:].strip()))
        elif search:
            context = context.filter(Purchase.name.like(search))
        items = {
            'draw': draw,
            'recordsTotal': context.count(),
            'recordsFiltered': context.count(),
            'data':
                []
            }
        for purchase_1 in context.offset(start).limit(length).all():
            items['data'].append({
                'id': purchase_1.id,
                'ref': purchase_1.ref,
                'supplier': purchase_1.supplier.name,
                'date': datetime.strftime(purchase_1.datetime, '%Y-%m-%d'),
                'quantity': int(db.session.query(db.func.sum(PurchasedItem.quantity)).filter(
                    PurchasedItem.purchase_id == purchase_1.id).scalar()),
                'amount': int(db.session.query(db.func.sum(PurchasedItem.cost_price)).filter(
                    PurchasedItem.purchase_id == purchase_1.id).scalar())
                })
        return jsonify(items)
    return render_template('purchase.html', title='Purchase')


@main.route('/purchase/view/<int:purchase_id>/', methods=['GET'])
@login_required
def purchase_detail(purchase_id):
    purchase_1 = Purchase.query.get_or_404(purchase_id)
    if purchase_1.company_id == current_user.company_id and not current_user.rights >=5:
        abort(403)

    return render_template('purchase_view.html', data=purchase_1)


@main.route('/purchase/add/', methods=['GET', 'POST'])
def purchase_add():
    from secrets import token_hex
    if request.method == 'POST':
        get_purchases = request.json
        import sys
        print(request.headers, file=sys.stdout)
        get_supplier_header = request.headers['SUPPLIER']  # get supplier id from header
        get_supplier = Supplier.query.get_or_404(get_supplier_header)  # get supplier from database
        if get_supplier:
            try:
                last_id = Purchase.query.order_by(Purchase.id.desc()).first().id
            except AttributeError:
                last_id = 1
            purchase_1 = Purchase(
                ref=f'{token_hex(3)}{last_id + 1}',
                company_id=current_user.company_id,
                supplier_id=get_supplier.id
            )
            db.session.add(purchase_1)
            db.session.flush()
            for item in get_purchases:
                description = item['description'].split(',')
                warehouse_id = WareHouse.query.filter_by(name=item['warehouse']).first_or_404()
                db.session.add(PurchasedItem(
                    purchase_id=purchase_1.id,
                    cost_price=item['price'],
                    name=item['name'],
                    quantity=item['quantity'],
                    size=description[0][6:],
                    color=description[1][7:],
                    warehouse_id=warehouse_id.id
                ))
                db.session.add(Item(
                    name=item['name'],
                    quantity=item['quantity'],
                    size=description[0][6:],
                    color=description[1][7:],
                    cost_price=item['price'],
                    wholesale_price=item['price'],
                    retail_price=item['price'],
                    added_by=current_user.id,
                    ware_house_id=warehouse_id.id,
                    company_id=current_user.company_id,
                    code=f'pur-{token_hex(3)}'
                ))
            db.session.commit()
            return jsonify({
                'status': True,
                'message': f'{len(get_purchases)} items purchased from {get_supplier.name} supplier.'
                })
        return jsonify({
            'status': False,
            'message': f'Failed'
        })
    warehouses = WareHouse.query.with_entities(WareHouse.id, WareHouse.name)\
        .filter_by(company_id=current_user.company_id, status=True).all()
    return render_template('add_purchase.html', title='Purchase', warehouses=warehouses)


@main.route('/purchase/get_supplier/')
def purchase_supplier_selection():
    suppliers = Supplier.query.filter_by(company_id=current_user.company_id, status=True).all()
    return render_template('list_suppliers.html', suppliers=suppliers)


@main.route('/media/<path:filename>')
def media(filename):
    return send_from_directory(app.config['MEDIA'], filename)


@main.route('/purchase/select/supplier/')
def purchase_select_supplier():
    return render_template('purchase_list_supplier.html')
