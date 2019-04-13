from flask import request, render_template, jsonify, abort
from datetime import datetime
from flask_login import current_user, login_required
from extensions import db
from ..people.models import Supplier
from ..main.models import PurchasedItem, Purchase
from . import inventory
from .models import Item, TransferItem, WareHouse


@inventory.route('/item/', methods=['GET', 'POST'])
@login_required
def item():
    if request.method == 'POST':
        from ..sale.models import InvoicedItem
        draw = int(request.form['draw'])
        start = int(request.form['start'])
        length = int(request.form['length'])
        search = request.form['search[value]']
        context = Item.query.filter_by(company_id=current_user.company_id, status=True)
        if search[:5] == 'code:':
            context = context.filter(Item.code.like(search[5:].strip()))
        elif search:
            context = context.filter(Item.name.like(search))
        items = {
            'draw': draw,
            'recordsTotal': context.count(),
            'recordsFiltered': context.count(),
            'data':
                [
                ]
            }
        for product in context.offset(start).limit(length).all():
            try:
                sold = int(db.session.query(db.func.sum(InvoicedItem.quantity)).filter(InvoicedItem.item_id == product.id)\
                           .scalar())
            except AttributeError and TypeError:
                sold = 0
            items['data'].append({
                'id': product.id,
                'code': product.code,
                'name': product.name,
                'warehouse': product.warehouse.name,
                'quantity': product.quantity,
                'sold': sold,
                'stock': product.quantity - sold,
                'date': product.datetime
                })
        return jsonify(items)
    return render_template('inventory/item.html', title='Items')


@inventory.route('/item/view/<int:item_id>', methods=['POST'])
@login_required
def item_view(item_id):
    item_1 = Item.query.get_or_404(item_id)
    if not current_user.company.id == item_1.company_id and not current_user.rights >= 2:
        abort(403)
    item_1.supplier = Supplier.query.get(item_1.supplier_id).name if item_1.supplier_id else '---'
    return render_template('inventory/item_view.html', data=item_1)


@inventory.route('item/add/', methods=['GET', 'POST'])
@login_required
def add():
    if request.method == 'POST':
        data = request.json
        ware_house = data['product-ware-house']
        name = data['product-name']
        supplier_id = data['product-supplier'] if data['product-supplier'] else None
        code = data['product-code']
        color = data['product-color']
        size = data['product-size']
        quantity = data['product-quantity']
        price = data['product-price']
        retail_price = data['product-retail-price']
        wholesale_price = data['product-wholesale-price']
        note = data['product-note']
        product_check = Item.query.filter_by(code=code, company_id=current_user.company_id,
                                             status=True).first()
        if product_check:
            return jsonify({
                'status': False,
                'message': f'Product {code} is already used with {product_check.name}.'
            })
        product_1 = Item(
            ware_house_id=ware_house,
            name=name,
            supplier_id=supplier_id,
            company_id=current_user.company_id,
            code=code,
            color=color,
            size=size,
            quantity=int(quantity),
            cost_price=int(price),
            retail_price=int(retail_price),
            wholesale_price=int(wholesale_price),
            added_by=current_user.id,
            note=note
        )
        db.session.add(product_1)
        db.session.commit()
        return jsonify({
            'status': True,
            'message': f'Product {name} has been added successfully.'
        })
    try:
        new_code = f'{Item.query.order_by(Item.id.desc()).first().id + 1}'
    except:
        new_code = 1
    ware_houses = WareHouse.query.filter_by(company_id=current_user.company_id, status=True).all()
    return render_template('inventory/add_item.html', title='Add Item', code=new_code, ware_houses=ware_houses)


@inventory.route('/item/edit/<int:item_id>', methods=['POST', 'PUT', 'DELETE'])
@login_required
def item_edit(item_id):
    product = Item.query.get_or_404(item_id)
    supplier_i = Supplier.query.filter_by(company_id=current_user.company_id).all()
    if product:
        if not Item.company_id == current_user.rights and not current_user.rights >= 4:
            abort(403)
    if request.method == 'POST':
        return render_template('inventory/edit_item.html', data=product, suppliers=supplier_i)
    if request.method == 'PUT':
        data = request.json
        product.supplier_id = data['supplier']
        product.name = data['name']
        product.color = data['color']
        product.size = data['size']
        product.quantity = data['quantity']
        product.cost_price = data['cost_price']
        product.wholesale_price = data['wholesale_price']
        product.retail_price = data['retail_price']
        product.notes = data['notes']
    if request.method == 'DELETE':
        product.status = False
    db.session.commit()
    return jsonify(
        {
            'message': f'Product { product.name } modified.',
            'status': True
        }
    )


@inventory.route('/item/check-code/<string:code>', methods=['POST'])
def check_product_code(code):
    product_code_check = Item.query.filter_by(code=code).first()
    if product_code_check:
        custom_error_msg = f'Product code "{ code }" is already used by { product_code_check.name }.'
        return jsonify({'status': False, 'message': custom_error_msg})
    return jsonify({'status': True, 'message': 'Okay'})


@inventory.route('/item/supplier/<int:supplier_id>', methods=['POST'])
@login_required
def get_item(supplier_id):
    item_1 = db.session.query(PurchasedItem).join(Purchase)\
        .filter(Purchase.company_id == current_user.company_id, Purchase.supplier_id == supplier_id).all()
    if not item_1 and not Supplier.query.filter_by(id=supplier_id, company_id=current_user.company_id).first():
        abort(403)
    data = []
    for each_item in item_1:
        data.append({
            'id': each_item.id,
            'name': each_item.name,
            'quantity': each_item.quantity,
            'color': each_item.color,
            'size': each_item.size,
            'price': each_item.cost_price
        })
    return jsonify(data)


@inventory.route('/item/warehouse/<int:warehouse_id>', methods=['POST'])
@login_required
def warehouse_products(warehouse_id):
    from ..sale.models import InvoicedItem
    item_1 = Item.query.filter_by(ware_house_id=warehouse_id, company_id=current_user.company_id, status=True).all()
    '''item_1 = db.session.query(Item).join(InvoicedItem)\
        .having(Item.quantity > db.func.sum(InvoicedItem.quantity))\
        .filter(Item.ware_house_id == warehouse_id, Item.company_id == current_user.company_id).all()'''
    data = []
    for each_item in item_1:
        data.append({
            'id': each_item.id,
            'name': each_item.name,
            'quantity': each_item.quantity,
            'color': each_item.color,
            'size': each_item.size,
            'retail_price': each_item.retail_price,
            'wholesale_price': each_item.wholesale_price,
            'description': f'Size: {each_item.size if each_item.size else "--"},\
            Model: {each_item.model if each_item.model else "--"}, Color: {each_item.color if each_item.color else "--"}',
        })
    return jsonify(data)


@inventory.route('/transfer/', methods=['GET', 'POST'])
@login_required
def transfer():
    if request.method == 'POST':
        draw = int(request.form['draw'])
        start = int(request.form['start'])
        length = int(request.form['length'])
        search = request.form['search[value]']
        context = TransferItem.query.filter_by(company_id=current_user.company_id)
        if search[:5] == 'code:':
            context.filter(TransferItem.ref.like(search[5:].strip()))
        elif search:
            context.filter(TransferItem.name.like(search))
        context.order_by()
        items = {
            'draw': draw,
            'recordsTotal': context.count(),
            'recordsFiltered': context.count(),
            'data':
                [
                ]
            }
        for transfer_1 in context.offset(start).limit(length).all():
            items['data'].append({
                'warehouse_from': transfer_1.warehouse_from.name,
                'warehouse_to': transfer_1.warehouse_to.name,
                'transferred_by': f'{ transfer_1.user.first_name } { transfer_1.user.first_name }',
                'quantity': len(transfer_1.quantity.split(',')),
                'date': datetime.strftime(transfer_1.datetime, '%Y-%m-%d')
                })
        return jsonify(items)
    return render_template('inventory/transfer.html', title='Transfer Item')


@inventory.route('/transfer/<int:t_from>/<int:t_to>', methods=['GET', 'POST'])
@login_required
def transfer_add(t_from, t_to):
    from ..inventory.models import WareHouse, Item, TransferedItem
    warehouses = WareHouse.query.filter(WareHouse.id.in_([t_from, t_to]))\
        .filter_by(company_id=current_user.company_id)
    if not warehouses.count() == 2:
        abort(400)
    if request.method == 'POST':
        items = request.json
        transfer_1 = TransferItem(
            company_id=current_user.company_id,
            staff=current_user.id,
            warehouse_from_id=t_from,
            warehouse_to_id=t_from,
            notes=items['notes']
        )
        db.session.add(transfer_1)
        db.session.flush()
        for each_item in items:
            get_item_1 = Item.query.filter_by(name=each_item['product']).first()
            if get_item_1:
                db.session.add(
                    TransferedItem(
                        transfer_id=transfer_1.id,
                        item_id=get_item.id,
                        quantity=item['quantity'],
                    ))
                get_item.quantity -= each_item['quantity']
                db.session.add(
                    db.session.expunge(get_item)

                )
            else:
                return jsonify({
                    'status': False,
                    'message': f"{item['name']} not found."
                })
        db.session.commit()
        return jsonify({
            'status': True,
            'message': f'Items transferred from {t_from} to {t_to}.',
            'transfer_id': transfer_1.id
        })
    products = Item.query.filter_by(company_id=current_user.company_id, ware_house_id=t_to).all()
    return render_template('inventory/transfer_add.html', products=products)


@inventory.route('/transfer/add/from/', defaults={'t_from': 0})
@inventory.route('/transfer/add/from/<int:t_from>', methods=['POST'])
@login_required
def transfer_add_selection(t_from):
    warehouses = WareHouse.query.filter_by(company_id=current_user.company_id) \
        .filter(~WareHouse.id.in_([t_from])).all()
    if request.method == 'POST':
        warehouses_to = []
        for each_warehouse_to in warehouses:
            warehouses_to.append(
                {
                    'id': each_warehouse_to.id,
                    'name': each_warehouse_to.name
                })
        return jsonify(warehouses_to)
    return render_template('inventory/transfer_warehouse_selection.html', warehouses=warehouses)
