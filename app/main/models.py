from extensions import db
from datetime import datetime
from sqlalchemy import inspect


class Purchase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id', ondelete='CASCADE'), nullable=False)
    supplier_id = db.Column(db.Integer, db.ForeignKey('supplier.id', ondelete='CASCADE'), nullable=False)
    ref = db.Column(db.String(40), nullable=False)
    datetime = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    item = db.relationship('PurchasedItem', backref='ref', lazy=True)


class PurchasedItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    purchase_id = db.Column(db.Integer, db.ForeignKey('purchase.id', ondelete='CASCADE'), nullable=False)
    warehouse_id = db.Column(db.Integer, db.ForeignKey('ware_house.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.String(40), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    cost_price = db.Column(db.Integer, nullable=False)
    size = db.Column(db.String(10))
    color = db.Column(db.String(20))


class Tax(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.String(40), nullable=False)
    percent = db.Column(db.Integer, nullable=False)


class Discount(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.String(40), nullable=False)
    percent = db.Column(db.Integer, nullable=False)


class Billing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id', ondelete='CASCADE'), nullable=False)
    datetime = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    amount = db.Column(db.Integer, nullable=False, default=0)


def sendmail(email_to, subject, message):  # Send email
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    from flask_login import current_user
    import smtplib
    smtp_host = current_user.company.smtp_host
    smtp_port = current_user.company.smtp_port
    smtp_email = current_user.company.email
    smtp_password = current_user.company.smtp_password
    msg = MIMEMultipart()
    msg['From'] = f'{current_user.company.name} <{smtp_email}>'
    msg['To'] = email_to
    msg['Subject'] = subject
    msg.attach(MIMEText(message, 'plain'))
    server = smtplib.SMTP(smtp_host, int(smtp_port))
    server.starttls()
    server.login(smtp_email, smtp_password)
    body = msg.as_string()
    server.sendmail(smtp_email, email_to, body)
    server.quit()


class Utils:

    @staticmethod
    def serialize_object(object_):
        return {c: getattr(object_, c) for c in inspect(object_).attrs.keys()}

    @staticmethod
    def serialize_object_list(object_list):
        return [{c: getattr(each, c) for c in inspect(each).attrs.keys()} for each in object_list]
