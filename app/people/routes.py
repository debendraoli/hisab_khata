from flask import request, render_template, jsonify, abort
from flask_login import current_user, login_required
from extensions import db, bcrypt
from ..auth.models import User
from . import people
from .models import Customer, Supplier, Staff, serialize
from secrets import token_hex


@people.route('/staff/', methods=['GET', 'POST'])
@login_required
def staff():
    if request.method == 'POST':
        draw = int(request.form['draw'])
        start = int(request.form['start'])
        length = int(request.form['length'])
        search = request.form['search[value]']
        context = User.query.filter(User.company_id == current_user.company_id)\
            .order_by()
        if search[:5] == 'code:':
            context = User.query.filter(User.company_id == current_user.company_id)\
                .filter(User.id.like(search[5:].strip()))\
                .order_by()
        elif search:
            context = User.query.filter(User.company_id == current_user.company_id) \
                    .filter(User.name.like(search)) \
                    .order_by()
        items = {
            'draw': draw,
            'recordsTotal': context.count(),
            'recordsFiltered': context.count(),
            'data': []
            }
        for user_1 in context.offset(start).limit(length).all():
            items['data'].append({
                'id': user_1.id,
                'staff_id': user_1.staff.staff_id,
                'name': f'{ user_1.first_name } { user_1.last_name }',
                'status': user_1.staff.status,
                'department': user_1.company.warehouse.filter_by(id=user_1.staff.warehouse_id).first().name,
                'address': user_1.staff.address,
                'email': user_1.email,
                'phone': user_1.staff.phone,
                'salary': user_1.staff.salary,
                })
        return jsonify(items)
    return render_template('people/staff.html', title='Staff')


@people.route('/staff/add/', methods=['GET', 'POST'])
@login_required
def staff_add():
    if request.method == 'POST':
        from ..main.models import sendmail
        data = request.json
        first_name = data['first_name']
        last_name = data['last_name']
        address = data['address']
        phone = data['phone']
        email = data['email']
        salary = data['salary']
        staff_id = data['staff_id']
        rights = data['rights']
        warehouse = data['warehouse']
        notes = data['notes']
        pw_raw = token_hex(4)
        pw_hashed = bcrypt.generate_password_hash(pw_raw)

        user_1 = User(
            company_id=current_user.company_id,
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=pw_hashed,
            rights=rights
        )
        db.session.add(user_1)
        db.session.flush()

        staff_1 = Staff(
            company_id=current_user.company_id,
            user_id=user_1.id,
            salary=salary,
            staff_id=staff_id,
            address=address,
            phone=phone,
            warehouse_id=warehouse,
            notes=notes
        )
        db.session.add(staff_1)
        db.session.commit()

        mail_subject = f'{current_user.company.name} Staff Registration.'
        mail_msg =\
            f'''Hi {first_name} {last_name},\n
            { current_user.company.name} has added you as employee.\n
            You password is {pw_raw}\n
            Please keep your password confidential.
            To login go to https://necommerce.online/login/'''
        sendmail(email, mail_subject, mail_msg)

        return jsonify(
            {
                'status': True,
                'message': f'Staff {first_name} added successfully. Password is send to the staff email address.'
            }
        )
    last_staff = Staff.query.with_entities(Staff.staff_id, Staff.salary).\
        filter_by(company_id=current_user.company_id).order_by(Staff.staff_id.desc()).first()
    warehouses = current_user.company.warehouse.all()
    return render_template('people/add_staff.html', last_staff=last_staff, warehouses=warehouses)


@people.route('/staff/edit/<int:staff_id>', methods=['POST', 'PUT', 'DELETE'])
@login_required
def staff_edit(staff_id):
    staff_1 = User.query.get_or_404(staff_id)
    if request.method == 'POST':
        return render_template('people/edit_staff.html', data=staff_1)
    if request.method == 'PUT':
        if not staff_1.company_id == current_user.company_id and not current_user.rights >= 4:
            abort(403)
        action = 'edited'
        data = request.json
        first_name = data['first_name']
        last_name = data['last_name']
        address = data['address']
        phone = data['phone']
        email = data['email']
        salary = data['salary']
        staff_id = data['staff_id']
        rights = data['rights']
        warehouse = data['warehouse']
        notes = data['notes']
        pw_raw = token_hex(4)
        pw_hashed = bcrypt.generate_password_hash(pw_raw)

        first_name = first_name
        last_name = last_name
        address = address
        phone = phone
        email = email
        salary = salary
        staff_id = staff_id
        rights = rights
        warehouse = warehouse
        notes = notes
        pw_raw = token_hex(4)
        pw_hashed = bcrypt.generate_password_hash(pw_raw)
    if request.method == 'DELETE':
        action = 'deleted'
        db.session.delete(staff_1)

    db.session.commit()
    return jsonify(
        {
            'status': True,
            'message': f'{staff_1.name} {action} successfully.'
        }
    )


@people.route('/staff/check/<string:field>/<value>', methods=['POST'])
@login_required
def check_staff_existent(field, value):
    if field == 'email':
        existent = User.query.with_entities(User.email).filter_by(email=value).first()
    elif field == 'staff_id':
        existent = Staff.query.filter_by(company_id=current_user.company_id, staff_id=value).first()
    if existent:
        return jsonify(
            {
                'status': False,
                'message': f'"{value}" is already used.'
            }
        )
    return jsonify(
            {
                'status': True,
                'message': 'Valid'
            }
        )


@people.route('/customer/', methods=['GET', 'POST'])
@login_required
def customer():
    if request.method == 'POST':
        draw = int(request.form['draw'])
        start = int(request.form['start'])
        length = int(request.form['length'])
        search = request.form['search[value]']
        context = Customer.query.filter(Customer.company_id == current_user.company_id) \
            .order_by()
        if search[:5] == 'code:':
            context = Customer.query.filter(Customer.company_id == current_user.company_id) \
                .filter(Customer.id.like(search[5:].strip())) \
                .order_by()
        elif search:
            context = Customer.query.filter(Customer.company_id == current_user.company_id) \
                .filter(Customer.name.like(search)) \
                .order_by()
        items = {
            'draw': draw,
            'recordsTotal': context.count(),
            'recordsFiltered': context.count(),
            'data': []
        }
        for customer_1 in context.offset(start).limit(length).all():
            items['data'].append({
                'id': customer_1.id,
                'name': customer_1.name,
                'status': customer_1.status,
                'address': customer_1.address,
                'email': customer_1.email,
                'phone': customer_1.phone,
                'last_order': customer_1.order[-1].ref if customer_1.order else '---',
            })
        return jsonify(items)
    return render_template('people/customer.html', title='Customers')


@people.route('/customer/add/', methods=['GET', 'POST'])
@login_required
def customer_add():
    if request.method == 'POST':
        data = request.json
        name = data['name']
        address = data['address']
        phone = data['phone']
        email = data['email']
        note = data['notes']

        customer_1 = Customer(
            company_id=current_user.company_id,
            name=name,
            address=address,
            phone=phone,
            email=email,
            note=note
        )
        db.session.add(customer_1)
        db.session.commit()
        return jsonify(
            {
                'status': True,
                'customer_id': customer_1.id,
                'message': f'Customer {name} added successfully.'
            }
        )
    return render_template('people/add_customer.html')


@people.route('/customer/edit/<int:customer_id>', methods=['POST', 'PUT', 'DELETE'])
@login_required
def customer_edit(customer_id):
    customer_1 = Customer.query.get_or_404(customer_id)
    if not customer_1.company_id == current_user.company_id and not current_user.rights >= 4:
        abort(403)
    if request.method == 'POST':
        return render_template('people/edit_customer.html', data=customer_1)
    if request.method == 'PUT':
        action = 'edited'
        data = request.json
        name = data['name']
        address = data['address']
        phone = data['phone']
        email = data['email']
        note = data['notes']

        customer_1.name = name
        customer_1.address = address
        customer_1.phone = phone
        customer_1.email = email
        customer_1.note = note
    if request.method == 'DELETE':
        action = 'deleted'
        customer_1.status = False

    db.session.commit()
    return jsonify(
        {
            'status': True,
            'message': f'{customer_1.name} {action} successfully.'
        }
    )


@people.route('/customer/list/', methods=['POST'])
@login_required
def customer_list():
    get_customers = Customer.query.filter_by(company_id=current_user.company_id).all()

    return jsonify([{'id': cust.id, 'name': cust.name} for cust in get_customers])


@people.route('/supplier/', methods=['GET', 'POST'])
@login_required
def supplier():
    if request.method == 'POST':
        draw = int(request.form['draw'])
        start = int(request.form['start'])
        length = int(request.form['length'])
        search = request.form['search[value]']
        context = Supplier.query.filter(Supplier.company_id == current_user.company_id)\
            .order_by()
        if search[:5] == 'code:':
            context = Supplier.query.filter(Supplier.company_id == current_user.company_id)\
                .filter(Supplier.id.like(search[5:].strip()))\
                .order_by()
        elif search:
            context = Supplier.query.filter(Supplier.company_id == current_user.company_id) \
                    .filter(Supplier.name.like(search)) \
                    .order_by()
        items = {
            'draw': draw,
            'recordsTotal': context.count(),
            'recordsFiltered': context.count(),
            'data': []
            }
        for supplier_1 in context.offset(start).limit(length).all():
            items['data'].append({
                'id': supplier_1.id,
                'name': supplier_1.name,
                'status': supplier_1.status,
                'address': supplier_1.address,
                'email': supplier_1.email,
                'phone': supplier_1.phone,
                'last_trade': supplier_1.purchase.ref if supplier_1.purchase else '---',
                })
        return jsonify(items)
    return render_template('people/supplier.html', title='Supplier')


@people.route('/supplier/add/', methods=['GET', 'POST'])
@login_required
def supplier_add():
    if request.method == 'POST':
        data = request.json
        name = data['name']
        address = data['address']
        phone = data['phone']
        email = data['email']
        sites = data['sites']
        description = data['description']

        supplier_1 = Supplier(
            company_id=current_user.company_id,
            name=name,
            address=address,
            phone=phone,
            email=email,
            sites=sites,
            description=description
        )
        db.session.add(supplier_1)
        db.session.commit()
        return jsonify(
            {
                'status': True,
                'message': f'Supplier {name} added successfully.',
                'supplier_id': supplier_1.id
            }
        )
    return render_template('people/add_supplier.html')


@people.route('/supplier/edit/<int:supplier_id>', methods=['POST', 'PUT', 'DELETE'])
@login_required
def supplier_edit(supplier_id):
    supplier_1 = Supplier.query.get_or_404(supplier_id)
    from json import loads
    load_sites = loads(supplier_1.sites)
    supplier_1.website = load_sites['website']
    supplier_1.facebook = load_sites['facebook']
    supplier_1.others = load_sites['others']
    if request.method == 'POST':
        return render_template('people/edit_supplier.html', data=supplier_1)
    if request.method == 'PUT':
        if not supplier_1.company_id == current_user.company_id and not current_user.rights >= 4:
            abort(403)
        action = 'edited'
        data = request.json
        name = data['name']
        address = data['address']
        phone = data['phone']
        email = data['email']
        sites = data['sites']
        description = data['description']

        supplier_1.name = name
        supplier_1.address = address
        supplier_1.phone = phone
        supplier_1.email = email
        supplier_1.sites = sites
        supplier_1.description = description
    if request.method == 'DELETE':
        action = 'deleted'
        db.session.delete(supplier_1)

    db.session.commit()
    return jsonify(
                {
                    'status': True,
                    'message': f'{supplier_1.name} { action } successfully.'
                }
            )


@people.route('/supplier/list/', methods=['POST'])
@login_required
def supplier_list():
    get_supplier = Supplier.query.filter_by(company_id=current_user.company_id, status=True).all()
    return jsonify([{'id': supp.id, 'name': supp.name} for supp in get_supplier])


@people.route('/supplier/get/', methods=['POST'])
@login_required
def get_supplier():
    suppliers = Supplier.query.filter_by(company_id=current_user.company_id).all()
    if not suppliers and not suppliers.company_id == current_user.company_id:
        abort(403)
    data = []
    for each_supplier in suppliers:
        data.append({
            'id': each_supplier.id,
            'name': each_supplier.name,
        })
    return jsonify(data)
