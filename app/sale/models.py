from extensions import db
from datetime import datetime


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ref = db.Column(db.String(40), nullable=False, index=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id', ondelete='CASCADE'), nullable=False)
    staff = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    datetime = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id', ondelete='CASCADE'), nullable=False,)
    status = db.Column(db.SmallInteger, default=1)
    remarks = db.Column(db.String(100))
    item = db.relationship('OrderedItem', backref='order', lazy=True)


class Invoice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ref = db.Column(db.String(40), nullable=False, index=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id', ondelete='CASCADE'), nullable=False)
    staff = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    datetime = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id', ondelete='CASCADE'), nullable=False)
    delivery_charge = db.Column(db.Integer, nullable=False, default=0)
    remarks = db.Column(db.String(100))
    discount_id = db.Column(db.Integer, db.ForeignKey('discount.id', ondelete=None))
    payment = db.relationship('Payment', backref='invoice', uselist=False, lazy=True)
    item = db.relationship('InvoicedItem', backref='invoice', lazy=True)
    shipment = db.relationship('Shipment', backref='invoice', lazy=True, uselist=False)
    discount = db.relationship('Discount')


class OrderedItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id', ondelete='CASCADE'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id', ondelete='CASCADE'), nullable=False)
    is_wholesale = db.Column(db.Boolean, nullable=False, default=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    discount_id = db.Column(db.Integer, db.ForeignKey('discount.id', ondelete=None), nullable=False, default=0)
    tax_id = db.Column(db.Integer, db.ForeignKey('tax.id', ondelete=None), nullable=False, default=0)
    item = db.relationship('Item', backref='ordered', lazy=True)
    discount = db.relationship('Discount')
    tax = db.relationship('Tax')


class InvoicedItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoice.id', ondelete='CASCADE'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id', ondelete='CASCADE'), nullable=False)
    is_wholesale = db.Column(db.Boolean, nullable=False, default=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    discount_id = db.Column(db.Integer, db.ForeignKey('discount.id', ondelete=None), nullable=False, default=0)
    tax_id = db.Column(db.Integer, db.ForeignKey('tax.id', ondelete=None), nullable=False, default=0)
    item = db.relationship('Item', backref='sold', lazy=True)
    discount = db.relationship('Discount')
    tax = db.relationship('Tax')


class Shipment(db.Model):
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoice.id', ondelete='CASCADE'), primary_key=True)
    ref = db.Column(db.String(40), nullable=False, default='Sh-', index=True)
    status = db.Column(db.SmallInteger, nullable=False, default=0)  # 0 = processing, 1 = returned, 2 = shipped
    datetime = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


def get_sales_by_range(company_id, day1, day2):
    return Invoice.query.filter(Invoice.company_id == company_id, Invoice.datetime.between(day1, day2)).all()


def profit_calculator(invoices):
    profit = 0
    if invoices:
        for invoice in invoices:
            for product in invoice.item:
                profit += product.item.wholesale_price - product.item.cost_price \
                    if product.is_wholesale else product.item.retail_price - product.item.cost_price
                profit -= product.discount.percent % 100 - product.tax.percent % 100
    return profit

