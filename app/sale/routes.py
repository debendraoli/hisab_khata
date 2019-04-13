from datetime import datetime
from flask import render_template, request, jsonify, abort
from flask_login import login_required, current_user
from extensions import db
from ..transaction.models import Payment
from . import sale
from .models import Order, Invoice, Shipment
from ..inventory.models import WareHouse, Item
from secrets import token_hex
from .models import InvoicedItem
from ..people.models import Customer


@sale.route('/order/', methods=['GET', 'POST'])
@login_required
def order():
    if request.method == 'POST':
        draw = int(request.form['draw'])
        start = int(request.form['start'])
        length = int(request.form['length'])
        search = request.form['search[value]']
        context = Order.query.filter_by(company_id=current_user.company_id)
        if search[:5] == 'code:':
            context = context.filter(Order.ref.like(search[5:].strip()))
        elif search:
            context = context.filter(Order.name.like(search))
        items = {
            'draw': draw,
            'recordsTotal': context.count(),
            'recordsFiltered': context.count(),
            'data':
                []
            }
        from ..sale.models import OrderedItem
        for order_1 in context.offset(start).limit(length).all():
            amount = 0
            try:
                quantity = int(db.session.query(db.func.sum(OrderedItem.quantity))
                               .filter(OrderedItem.order_id == order_1.id).scalar())
            except TypeError:
                quantity = 0
            for ordered_item in order_1.item:
                amount += ordered_item.item.wholesale_price * ordered_item.quantity \
                    if ordered_item.is_wholesale else ordered_item.item.retail_price * ordered_item.quantity
            items['data'].append({
                'id': order_1.id,
                'ref': order_1.ref,
                'name': order_1.customer.name,
                'quantity': quantity,
                'amount': amount,
                'date': datetime.strftime(order_1.datetime, '%Y-%m-%d'),
                'status': order_1.status
                })
        return jsonify(items)
    return render_template('sale/order.html', title='Orders')


@sale.route('/payment/', methods=['GET', 'POST'])
@login_required
def payment():
    if request.method == 'POST':
        draw = int(request.form['draw'])
        start = int(request.form['start'])
        length = int(request.form['length'])
        search = request.form['search[value]']
        context = Payment.query.filter(Payment.company_id == current_user.company_id)\
            .order_by()
        if search[:5] == 'code:':
            context = Payment.query.filter(Payment.company_id == current_user.company_id)\
                .filter(Payment.ref.like(search[5:].strip()))\
                .order_by()
        elif search:
            context = Payment.query.filter(Payment.company_id == current_user.company_id) \
                    .filter(Payment.name.like(search)) \
                    .order_by()
        items = {
            'draw': draw,
            'recordsTotal': context.count(),
            'recordsFiltered': context.count(),
            'data':
                [
                ]
            }
        for payment_1 in context.offset(start).limit(length).all():
            items['data'].append({
                'ref': payment_1.ref,
                'order_ref': payment_1.order.ref,
                'name': payment_1.order.customer.name,
                'method': payment_1.method.name,
                'quantity': len(payment_1.order.products.split(',')),
                'amount': payment_1.amount,
                'status': payment_1.status,
                'date': datetime.strftime(payment_1.datetime, '%Y-%m-%d')
                })
        return jsonify(items)
    return render_template('sale/payment.html', title='Payments')


@sale.route('/order/add/', methods=['GET', 'POST'])
def order_add():
    from ..inventory.models import WareHouse, Item
    from secrets import token_hex
    from .models import OrderedItem
    from ..people.models import Customer
    if request.method == 'POST':
        get_customer_id = request.headers.get('CUSTOMER')
        customer_1 = Customer.query.get_or_404(get_customer_id)
        items = request.json
        try:
            last_order = Order.query.order_by(Order.id.desc()).first().id
        except AttributeError:
            last_order = 0
        order_1 = Order(
            ref=f'{token_hex(3)}{last_order + 1}',
            company_id=current_user.company_id,
            staff=current_user.id,
            customer_id=customer_1.id,
            )
        db.session.add(order_1)
        db.session.flush()
        for item in items:
            get_item = Item.query.filter_by(name=item['product']).first()
            if get_item:
                is_wholesale = True if item['price'] == get_item.wholesale_price else False
                db.session.add(
                    OrderedItem(
                        order_id=order_1.id,
                        item_id=get_item.id,
                        quantity=item['quantity'],
                        discount_id=2,
                        is_wholesale=is_wholesale,
                        tax_id=2,
                    ))
            else:
                return jsonify({
                    'status': False,
                    'message': f"{item['name']} not found."
                })
        db.session.commit()
        return jsonify({
            'status': True,
            'message': f'Order Created for { customer_1.name }.',
            'order_id': order_1.id
        })
    ware_houses = WareHouse.query.filter_by(company_id=current_user.company_id, status=True).all()
    return render_template('sale/add_order.html', warehouses=ware_houses)


@sale.route('/invoice/', methods=['GET', 'POST'])
def invoice():
    if request.method == 'POST':
        draw = int(request.form['draw'])
        start = int(request.form['start'])
        length = int(request.form['length'])
        search = request.form['search[value]']
        context = Invoice.query.filter_by(company_id=current_user.company_id)
        if search[:5] == 'code:':
            context = context.filter(Invoice.ref.like(search[5:].strip()))
        elif search:
            context = context.filter(Invoice.name.like(search))
        context = context.order_by()
        items = {
            'draw': draw,
            'recordsTotal': context.count(),
            'recordsFiltered': context.count(),
            'data':
                []
        }
        from .models import InvoicedItem
        amount = 0
        for invoice_1 in context.offset(start).limit(length).all():
            try:
                quantity = int(db.session.query(db.func.sum(InvoicedItem.quantity))
                               .filter(InvoicedItem.invoice_id == invoice_1.id).scalar())
            except TypeError:
                quantity = 0
            for invoiced_item in invoice_1.item:
                amount += invoiced_item.item.wholesale_price * invoiced_item.quantity \
                    if invoiced_item.is_wholesale else invoiced_item.item.retail_price * invoiced_item.quantity

            items['data'].append({
                'ref': invoice_1.ref,
                'name': invoice_1.customer.name,
                'quantity': quantity,
                'amount': amount,
                'date': datetime.strftime(invoice_1.datetime, '%Y-%m-%d')
            })
        return jsonify(items)
    return render_template('sale/invoice.html', title='Invoice')


@sale.route('/invoice/add/', methods=['GET', 'POST'])
def invoice_add():
    if request.method == 'POST':
        get_customer_id = request.headers.get('CUSTOMER')
        customer_1 = Customer.query.get_or_404(get_customer_id)
        items = request.json
        try:
            last_invoice = Invoice.query.order_by(Invoice.id.desc()).first().id
        except AttributeError:
            last_invoice = 0
        invoice_1 = Invoice(
            ref=f'{token_hex(3)}{last_invoice + 1}',
            company_id=current_user.company_id,
            staff=current_user.id,
            customer_id=customer_1.id,
            delivery_charge=0,
            )
        db.session.add(invoice_1)
        db.session.flush()
        for item in items:
            get_item = Item.query.filter_by(name=item['product']).first()
            if get_item:
                is_wholesale = True if item['price'] == get_item.wholesale_price else False
                db.session.add(
                    InvoicedItem(
                        invoice_id=invoice_1.id,
                        item_id=get_item.id,
                        quantity=item['quantity'],
                        discount_id=2,
                        is_wholesale=is_wholesale,
                        tax_id=2,
                    ))
            else:
                return jsonify({
                    'status': False,
                    'message': f"{item['name']} not found."
                })
        db.session.commit()
        return jsonify({
            'status': True,
            'message': f'Invoice Created for { customer_1.name }.',
            'invoice_id': invoice_1.id
        })
    ware_houses = WareHouse.query.filter_by(company_id=current_user.company_id).all()
    return render_template('sale/add_invoice.html', warehouses=ware_houses)


@sale.route('/invoice/edit/<int:invoice_id>', methods=['GET', 'POST'])
def invoice_edit(invoice_id):
    if request.method == 'POST':
        get_customer_id = request.headers.get('CUSTOMER')
        customer_1 = Customer.query.get_or_404(get_customer_id)
        invoice_1 = Invoice.query.get_or_404(invoice_id)
        items = request.json
        for item in items:
            get_item = Item.query.filter_by(name=item['product']).first()
            get_invoiced_item = InvoicedItem.query.filter_by(name=item['product']).first()
            if get_item:
                is_wholesale = True if item['price'] == get_item.wholesale_price else False
                if not get_invoiced_item:
                    db.session.add(
                        InvoicedItem(
                            invoice_id=invoice_1.id,
                            item_id=get_item.id,
                            quantity=item['quantity'],
                            discount_id=2,
                            is_wholesale=is_wholesale,
                            tax_id=2,
                        ))
                else:
                    get_invoiced_item.quantity = item['quantity']
            else:
                return jsonify({
                    'status': False,
                    'message': f"{item['name']} not found."
                })
        db.session.commit()
        return jsonify({
            'status': True,
            'message': f'{ customer_1.name } invoice\'s modified for { customer_1.name }.',
            'invoice_id': invoice_1.id
        })
    ware_houses = WareHouse.query.filter_by(company_id=current_user.company_id).all()
    invoiced_items = InvoicedItem.query.filter_by(invoice_id=invoice_id).all()
    return render_template('sale/invoice_view.html', warehouses=ware_houses, invoiced_items=invoiced_items)


@sale.route('/shipment/', methods=['GET', 'POST'])
def shipment():
    if request.method == 'POST':
        draw = int(request.form['draw'])
        start = int(request.form['start'])
        length = int(request.form['length'])
        search = request.form['search[value]']
        context = Shipment.query.filter_by(company_id=current_user.company_id)\
            .order_by()
        if search[:5] == 'code:':
            context = Shipment.query.filter_by(company_id=current_user.company_id) \
                .filter(Invoice.ref.like(search[5:].strip())) \
                .order_by()
        elif search:
            context = Invoice.query.filter(Invoice.company_id == current_user.company_id) \
                .filter(Invoice.name.like(search)) \
                .order_by()
        items = {
            'draw': draw,
            'recordsTotal': context.count(),
            'recordsFiltered': context.count(),
            'data':
                []
        }
        from .models import InvoicedItem
        amount = 0
        for invoice_1 in context.offset(start).limit(length).all():
            quantity = int(db.session.query(db.func.sum(InvoicedItem.quantity))
                           .filter(InvoicedItem.invoice_id == invoice_1.id).scalar())
            for invoiced_item in invoice_1.items:
                amount += invoiced_item.item.wholesale_price * invoiced_item.quantity \
                    if invoice_1.is_wholesale else invoiced_item.item.retail_price * invoiced_item.quantity
            items['data'].append({
                'ref': invoice_1.shipment.ref,
                'invoice_ref': invoice_1.ref,
                'name': invoice_1.customer.name,
                'quantity': quantity,
                'amount': amount,
                'status': invoice_1.shipment.status,
                'address': invoice_1.customer.address,
                'date': datetime.strftime(invoice_1.shipment.datetime, '%Y-%m-%d')
            })
        return jsonify(items)
    return render_template('sale/shipment.html')


@sale.route('/shipment/<int:invoice_id>')
def shipment_add(invoice_id):
    # todo
    return render_template('')


@sale.route('/invoice/view/<int:invoice_id>')
def invoice_view(invoice_id):
    from .models import InvoicedItem
    from ..inventory.models import Item
    invoice_1 = Invoice.query.get(invoice_id)
    total = 0
    discount_total = 0
    tax_total = 0
    for item in invoice_1.item:
        discount = item.discount.percent % item.item.wholesale_price if item.is_wholesale\
            else item.discount.percent % item.item.retail_price
        tax = item.tax.percent % item.item.wholesale_price if item.is_wholesale\
            else item.tax.percent % item.item.retail_price
        total += db.session.query(db.func.sum(InvoicedItem.quantity * Item.wholesale_price if item.is_wholesale
                                              else InvoicedItem.quantity * Item.retail_price))\
            .filter(InvoicedItem.invoice_id == invoice_1.id).scalar()
        discount_total += discount
        tax_total += tax

    data = {
        'ref': invoice_1.ref,
        'customer': invoice_1.customer,
        'items': invoice_1.item,
        'datetime': invoice_1.datetime,
        'tax_total': tax_total,
        'tax_percent': tax_total / total * 100,
        'discount_total': discount_total,
        'discount_percent': discount_total / total * 100,
        'subtotal': total,
        'total': total - tax_total - discount_total
    }
    return render_template('sale/invoice_print.html', data=data, items=invoice_1.item)


@sale.route('/invoice/print/<int:invoice_id>')
def invoice_print(invoice_id):
    from .models import InvoicedItem
    from ..inventory.models import Item
    invoice_1 = Invoice.query.get_or_404(invoice_id)
    if not invoice_1.company_id == current_user.company_id:
        abort(403)
    total = 0
    discount_total = 0
    tax_total = 0
    for item in invoice_1.item:
        discount = item.discount.percent % item.item.wholesale_price if item.is_wholesale\
            else item.discount.percent % item.item.retail_price
        tax = item.tax.percent % item.item.wholesale_price if item.is_wholesale\
            else item.tax.percent % item.item.retail_price
        total += db.session.query(db.func.sum(InvoicedItem.quantity * Item.wholesale_price if item.is_wholesale
                                              else InvoicedItem.quantity * Item.retail_price))\
            .filter(InvoicedItem.invoice_id == invoice_1.id).scalar()
        discount_total += discount
        tax_total += tax

    data = {
        'ref': invoice_1.ref,
        'customer': invoice_1.customer,
        'datetime': invoice_1.datetime,
        'tax_total': tax_total,
        'tax_percent': tax_total / total * 100,
        'discount_total': discount_total,
        'discount_percent': discount_total / total * 100,
        'subtotal': total,
        'total': total - tax_total - discount_total
    }
    return render_template('sale/invoice_print.html', data=data, items=invoice_1.item)


@sale.route('/order/print/<int:order_id>')
def order_print(order_id):
    from .models import OrderedItem
    from ..inventory.models import Item
    order_1 = Order.query.get_or_404(order_id)
    total = 0
    discount_total = 0
    tax_total = 0
    for item in order_1.item:
        discount = item.discount.percent % item.item.wholesale_price if item.is_wholesale\
            else item.discount.percent % item.item.retail_price
        tax = item.tax.percent % item.item.wholesale_price if item.is_wholesale\
            else item.tax.percent % item.item.retail_price
        total += db.session.query(db.func.sum(OrderedItem.quantity * Item.wholesale_price if item.is_wholesale
                                              else OrderedItem.quantity * Item.retail_price))\
            .filter(OrderedItem.order_id == order_1.id).scalar()
        discount_total += discount
        tax_total += tax

    data = {
        'ref': order_1.ref,
        'customer': order_1.customer,
        'datetime': order_1.datetime,
        'tax_total': tax_total,
        'tax_percent': tax_total / total * 100,
        'discount_total': discount_total,
        'discount_percent': discount_total / total * 100,
        'subtotal': total,
        'total': total - tax_total - discount_total
    }
    return render_template('sale/order_print.html', data=data, items=order_1.item)











@sale.route('/set_customer/<string:type>', methods=['POST'])
def set_customer(type):
    customers_all = ''
    return render_template(f'sale/list_customer_{type}.html', data=customers_all)

