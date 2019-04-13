from extensions import db
from datetime import datetime
from sqlalchemy import inspect


class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id', ondelete='CASCADE'))
    status = db.Column(db.Boolean, default=True, index=True)
    datetime = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    name = db.Column(db.String(50))
    address = db.Column(db.String(80))
    phone = db.Column(db.String(13), nullable=False)
    email = db.Column(db.String(40))
    note = db.Column(db.String(100))
    invoice = db.relationship('Invoice', backref='customer', lazy=True)
    order = db.relationship('Order', backref='customer', lazy=True)


class Staff(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    warehouse_id = db.Column(db.Integer, db.ForeignKey('ware_house.id', ondelete='CASCADE'), nullable=False)
    staff_id = db.Column(db.Integer, nullable=False)
    address = db.Column(db.String(80), nullable=False)
    phone = db.Column(db.String(13), nullable=False)
    status = db.Column(db.SmallInteger, default=0)  # 1 = leave, 2 = vacation
    notes = db.Column(db.String(100), default=0)
    salary = db.Column(db.Integer, nullable=False)


class StaffSalary(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    staff_id = db.Column(db.Integer, db.ForeignKey('staff.user_id', ondelete='CASCADE'), nullable=False)
    datetime = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    paid_by = db.Column(db.Integer, db.ForeignKey('staff.user_id'), nullable=False)
    staff = db.relationship(Staff, backref='salary_info', lazy=True, foreign_keys=[staff_id])


class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    address = db.Column(db.Text, default='{"address_1": "", "address_2": ""}')
    status = db.Column(db.SmallInteger, default=0)  # 1 = active, 2 = no credit
    currency = db.Column(db.SmallInteger, default=0)  # default = Rupee, 2 = USD
    logo = db.Column(db.String(20), default='default')
    phone = db.Column(db.Text, default='{"phone_1": "", "phone_2": ""}')
    email = db.Column(db.String(40), nullable=False)
    smtp_host = db.Column(db.String(100), nullable=False, default='smtp.google.com')
    smtp_password = db.Column(db.String(40), nullable=False)
    smtp_port = db.Column(db.Integer, nullable=False, default=25)
    sites = db.Column(db.Text, default='{"facebook": "", "instagram": "", "website": ""}')
    credits = db.Column(db.Integer, nullable=False, default=0)
    setting = db.Column(db.Text, nullable=False, default='{"currency_symbol": ""}')
    datetime = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    timezone = db.Column(db.String(50), nullable=False)
    user = db.relationship('User', backref='company', lazy=True)
    warehouse = db.relationship('WareHouse', backref='company', lazy='dynamic')


class Supplier(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.Boolean, default=True, index=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.String(40), nullable=False)
    address = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(13), nullable=False)
    email = db.Column(db.String(40))
    sites = db.Column(db.Text, default='{"website": "", "facebook": "", "others": ""}')
    description = db.Column(db.String(100))
    datetime = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    purchase = db.relationship('Purchase', backref='supplier', lazy=True, uselist=False)


class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    from_user = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))
    datetime = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    status = db.Column(db.Boolean, default=False, nullable=False)
    type = db.Column(db.SmallInteger, default=0)  # 0 = normal
    title = db.Column(db.String(80), nullable=False)
    content = db.Column(db.Text, nullable=False)
    user = db.relationship('User', backref='notification', lazy=True, foreign_keys=[user_id])


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(80), nullable=False)
    priority = db.Column(db.SmallInteger, default=0)
    status = db.Column(db.Integer, nullable=False)
    datetime = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user = db.relationship('User', backref='tasks')


class ToDo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))
    title = db.Column(db.String(100))
    status = db.Column(db.Boolean, default=True)


def serialize(object_):
    # @ returns dictionary object with model field name as key
    return [{c: getattr(each, c) for c in inspect(each).attrs.keys()} for each in object_]
