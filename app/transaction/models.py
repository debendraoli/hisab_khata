from extensions import db
from datetime import datetime


class PaymentMethod(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id', ondelete='CASCADE'))
    status = db.Column(db.Boolean, default=True, index=True)
    name = db.Column(db.String(50), nullable=False, index=True)  # bank name, paypal, stripe, Cash on delivery, etc
    account = db.Column(db.String(50))
    holder_name = db.Column(db.String(50), nullable=False)
    api = db.Column(db.String(100))


class Payment(db.Model):
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoice.id', ondelete='CASCADE'), primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id', ondelete='CASCADE'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id', ondelete='CASCADE'), nullable=False)
    method_id = db.Column(db.Integer, db.ForeignKey('payment_method.id', ondelete='CASCADE'), nullable=False)
    status = db.Column(db.Boolean, nullable=False, default=False)
    amount = db.Column(db.Integer, nullable=False)
    ref = db.Column(db.String(40), nullable=False)
    datetime = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    method = db.relationship(PaymentMethod, lazy=True)


class ExpenseType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id', ondelete='CASCADE'))
    name = db.Column(db.String(40), nullable=False)


class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id', ondelete='CASCADE'), nullable=False)
    status = db.Column(db.Boolean, nullable=False, default=True)
    amount = db.Column(db.Integer, nullable=False)
    type = db.Column(db.Integer, db.ForeignKey('expense_type.id'), nullable=False)
    account = db.Column(db.Integer, db.ForeignKey('payment_method.id', ondelete='CASCADE'), nullable=False)
    datetime = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


class Deposit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    status = db.Column(db.Boolean, default=True, nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    datetime = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    account_id = db.Column(db.Integer, db.ForeignKey('payment_method.id', ondelete='CASCADE'), nullable=False)
    notes = db.Column(db.String(100))
    user = db.relationship('User')
    account = db.relationship(PaymentMethod, backref='deposit', lazy=True)



