from extensions import db
from datetime import datetime


class WareHouse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    status = db.Column(db.Boolean, default=True, nullable=False)
    code = db.Column(db.String(20), nullable=False, index=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(100))
    item = db.relationship('Item', lazy='dynamic', backref='warehouse')


class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ware_house_id = db.Column(db.Integer, db.ForeignKey('ware_house.id', ondelete='CASCADE'), nullable=False)
    supplier_id = db.Column(db.Integer)
    status = db.Column(db.Boolean, default=True, index=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id', ondelete='CASCADE'))
    name = db.Column(db.String(40), nullable=False)
    code = db.Column(db.String(20), nullable=False, index=True)
    datetime = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    color = db.Column(db.String(15))
    size = db.Column(db.String(15))
    model = db.Column(db.String(15))
    quantity = db.Column(db.Integer, nullable=False, index=True)
    added_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    note = db.Column(db.String(100))
    cost_price = db.Column(db.Integer, nullable=False)
    retail_price = db.Column(db.Integer, nullable=False)
    wholesale_price = db.Column(db.Integer, nullable=False)


class TransferItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id', ondelete='CASCADE'), nullable=False)
    warehouse_from_id = db.Column(db.Integer, db.ForeignKey('ware_house.id', ondelete='CASCADE'), nullable=False)
    warehouse_to_id = db.Column(db.Integer, db.ForeignKey('ware_house.id', ondelete='CASCADE'), nullable=False)
    datetime = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    notes = db.Column(db.String(100))
    warehouse_from = db.relationship(WareHouse, foreign_keys=[warehouse_from_id], lazy=True)
    warehouse_to = db.relationship(WareHouse, foreign_keys=[warehouse_to_id], lazy=True)
    user = db.relationship('User', lazy=True)


class TransferedItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    transfer_id = db.Column(db.Integer, db.ForeignKey('transfer_item.id', ondelete='CASCADE'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id', ondelete='CASCADE'), nullable=False)
