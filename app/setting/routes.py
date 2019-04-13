from flask import request, abort, jsonify, render_template
from flask_login import current_user, login_required
from extensions import db
from . import setting
from ..inventory.models import WareHouse, Item
from ..transaction.models import PaymentMethod, Deposit
from ..people.models import Company
from datetime import datetime


@setting.route('/warehouse/', methods=['GET', 'POST'])
@login_required
def warehouse():
    if request.method == 'POST':
        draw = int(request.form['draw'])
        start = int(request.form['start'])
        length = int(request.form['length'])
        search = request.form['search[value]']
        context = WareHouse.query.filter_by(company_id=current_user.company_id, status=True)\
            .order_by()
        if search[:5] == 'code:':
            context.filter(WareHouse.code.like(search[5:].strip()))
        elif search:
                context.filter(WareHouse.name.like(search))
        items = {
            'draw': draw,
            'recordsTotal': context.count(),
            'recordsFiltered': context.count(),
            'data':
                []
            }
        for warehouse_1 in context.offset(start).limit(length).all():
            items['data'].append({
                'id': warehouse_1.id,
                'code': warehouse_1.code,
                'name': warehouse_1.name,
                'total_stock': warehouse_1.item.filter(Item.quantity >= 1).count(),
                'total_stock_value': warehouse_1.name,
                'total_profit': warehouse_1.name,
                })
        return jsonify(items)
    return render_template('setting/warehouse.html', title='Warehouse')


@setting.route('/warehouse/add/', methods=['GET', 'POST'])
@login_required
def warehouse_add():
    if request.method == 'POST':
        data = request.json
        name = data['name']
        code = data['code']
        description = data['description']
        code_exists = WareHouse.query.filter_by(code=code, company_id=current_user.company_id).first()
        if code_exists:
            return jsonify({
                'status': False,
                'message': f'Warehouse {code} is already used with {code_exists.name}.'
            })
        warehouse_1 = WareHouse(
            name=name,
            company_id=current_user.company_id,
            code=code,
            description=description,
        )
        db.session.add(warehouse_1)
        db.session.commit()
        return jsonify({
            'status': True,
            'message': f'Warehouse {name} has been added successfully.'
        })
    try:
        new_code = f'IT-{WareHouse.query.order_by(WareHouse.id.desc()).first().id + 1}'
    except AttributeError:
        new_code = 1
    return render_template('setting/add_warehouse.html', title='Add Item', code=new_code)


@setting.route('/warehouse/edit/<int:warehouse_id>', methods=['POST', 'PUT', 'DELETE'])
@login_required
def warehouse_edit(warehouse_id):
    warehouse_1 = WareHouse.query.get_or_404(warehouse_id)
    if not warehouse_1.company_id == current_user.company_id and not current_user.rights >= 4:
        abort(403)
    if request.method == 'POST':
        return render_template('setting/edit_warehouse.html', data=warehouse_1)
    if request.method == 'PUT':
        data = request.json
        warehouse_1.name = data['name']
        warehouse_1.code = data['code']
        warehouse_1.description = data['description']
    if request.method == 'DELETE':
        warehouse_1.status = False
    db.session.commit()
    return jsonify(
        {
            'message': f'Warehouse { warehouse_1.name } modified.',
            'status': True
        }
    )


@setting.route('/information/', methods=['GET', 'POST'])
@login_required
def information():
    from ..main.models import Billing
    from pytz import common_timezones
    from datetime import timedelta, datetime
    data = Company.query.get(current_user.company_id)
    billings = Billing.query.filter_by(company_id=current_user.company_id).order_by(Billing.id.desc()).limit(10).all()
    billings_data = {
        'last_billed_date': billings[-1].datetime,
        'last_billed_amount': billings[-1].amount,
        'next_due_date': datetime.utcnow() + timedelta(current_user.company.credits),
        'days_remaining': current_user.company.credits,
        'all_billings': billings,
    }
    return render_template('setting/information.html', data=data, timezones=common_timezones,
                           billings=billings_data)


@setting.route('/bank-account/', methods=['GET', 'POST'])
@login_required
def bank_account():
    if request.method == 'POST':
        draw = int(request.form['draw'])
        start = int(request.form['start'])
        length = int(request.form['length'])
        search = request.form['search[value]']
        context = PaymentMethod.query.filter_by(company_id=current_user.company_id, status=True)\
            .order_by()
        if search:
            context = PaymentMethod.query.filter_by(company_id=current_user.company_id, status=True) \
                    .filter(PaymentMethod.name.like(search)) \
                    .order_by()
        items = {
            'draw': draw,
            'recordsTotal': context.count(),
            'recordsFiltered': context.count(),
            'data':
                []
            }
        for bank_account_1 in context.offset(start).limit(length).all():
            try:
                balance = int(db.session.query(db.func.sum(Deposit.amount))
                              .filter(Deposit.account_id == bank_account_1.id).scalar())
            except AttributeError and TypeError:
                balance = 0
            try:
                last_deposit_date = datetime.strftime(bank_account_1.deposit[-1].datetime, '%Y-%m-%d')
            except IndexError:
                last_deposit_date = '---'

            items['data'].append({
                'id': bank_account_1.id,
                'holder_name': bank_account_1.holder_name,
                'bank_name': bank_account_1.name,
                'balance': balance,
                'account': bank_account_1.account,
                'last_deposited': last_deposit_date
                })
        return jsonify(items)
    return render_template('setting/bank.html', title='Bank Accounts')


@setting.route('/bank-account/add/', methods=['GET', 'POST'])
@login_required
def bank_account_add():
    if request.method == 'POST':
        data = request.json
        holder_name = data['holder_name']
        bank_name = data['holder_name']
        account = data['account']
        api = data['api']
        code_exists = PaymentMethod.query.filter_by(account=account, company_id=current_user.company_id).first()
        if code_exists:
            return jsonify({
                'status': False,
                'message': f'Bank {account} is already used with {code_exists.holder_name}.'
            })
        bank_account_1 = PaymentMethod(
            holder_name=holder_name,
            name=bank_name,
            account=account,
            company_id=current_user.company_id,
            api=api
        )
        db.session.add(bank_account_1)
        db.session.commit()
        return jsonify({
            'status': True,
            'message': f'{bank_name}\'s {account} has been added successfully.'
        })
    return render_template('setting/bank_add.html', title='Add Bank')


@setting.route('/bank-account/edit/<int:bank_id>', methods=['POST', 'PUT', 'DELETE'])
@login_required
def bank_account_edit(bank_id):
    bank_1 = PaymentMethod.query.get_or_404(bank_id)
    if not bank_1.company_id == current_user.company_id and not current_user.rights >= 4:
        abort(403)
    if request.method == 'POST':
        return render_template('setting/bank_edit.html', data=bank_1)
    if request.method == 'PUT' and request.is_json:
        data = request.json
        bank_1.holder_name = data['holder_name']
        bank_1.name = data['bank_name']
        bank_1.api = data['api']
    if request.method == 'DELETE':
        bank_1.status = False
    db.session.commit()
    return jsonify(
        {
            'message': f'Bank { bank_1.account } modified.',
            'status': True
        }
    )


@setting.route('/change-timezone/', methods=['POST'])
@login_required
def change_timezone():
    data = request.json
    company_1 = Company.query.get_or_404(current_user.company_id)
    company_1.timezone = data
    db.session.commit()
    return jsonify({
        'status': True,
        'message': f'Timezone modified to { data }'
    })


@setting.route('/category/', methods=['GET', 'POST'])
def category():
    # todo
    return ''


@setting.route('/backup/', methods=['GET', 'POST'])
def backup():
    # todo
    return ''




