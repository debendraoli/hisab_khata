from datetime import datetime
from flask import request, render_template, jsonify
from flask_login import login_required, current_user
from extensions import db
from . import transaction
from .models import Deposit, PaymentMethod


@transaction.route('/deposits/', methods=['GET', 'POST'])
@login_required
def deposit():
    if request.method == 'POST':
        draw = int(request.form['draw'])
        start = int(request.form['start'])
        length = int(request.form['length'])
        search = request.form['search[value]']
        context = Deposit.query.filter_by(company_id=current_user.company_id, status=True)
        if search:
            context = context.filter(Deposit.user.name.like(search))
        items = {
            'draw': draw,
            'recordsTotal': context.count(),
            'recordsFiltered': context.count(),
            'data':
                []
        }
        for deposit_1 in context.offset(start).limit(length).all():
            items['data'].append({
                'id': deposit_1.id,
                'user': f'{ deposit_1.user.first_name} { deposit_1.user.last_name}',
                'bank_name': deposit_1.account.name,
                'account': deposit_1.account.account,
                'amount': deposit_1.amount,
                'datetime': datetime.strftime(deposit_1.datetime, '%Y-%m-%d'),
            })
        return jsonify(items)
    return render_template('trans/deposit.html', title='Deposits')


@transaction.route('/deposit/add/', methods=['GET', 'POST'])
@login_required
def deposit_add():
    if request.method == 'POST':
        data = request.json
        account_id = int(data['account'])
        amount = int(data['amount'])
        notes = data['notes']
        deposit_1 = Deposit(
            account_id=account_id,
            company_id=current_user.company_id,
            user_id=current_user.id,
            amount=int(amount),
            notes=notes,
        )
        db.session.add(deposit_1)
        db.session.commit()
        return jsonify({
            'status': True,
            'message': f'Amount deposited to {account_id}.'
        })
    accounts = PaymentMethod.query.filter_by(status=True, company_id=current_user.company_id).all()
    return render_template('trans/deposit_add.html', accounts=accounts, title='Add Deposit')


@transaction.route('/expense/')
@login_required
def expense():
    # todo
    return


@transaction.route('transfer/')
@login_required
def transfer():
    # todo
    return


@transaction.route('view/')
@login_required
def view():
    # todo
    return
