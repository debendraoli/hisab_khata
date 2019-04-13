from datetime import datetime
from pytz import timezone, utc as pytz_utc
from flask_login import UserMixin
from extensions import db, login_manager


@login_manager.user_loader
def load_user(user_id):
        return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(35))
    last_name = db.Column(db.String(35), nullable=False)
    status = db.Column(db.Boolean, default=False, index=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id', ondelete='CASCADE'), nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.Binary, nullable=False)
    rights = db.Column(db.Integer, default=0, index=True)
    photo = db.Column(db.String(20), nullable=False, default='default')
    added_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    last_logged = db.Column(db.DateTime)
    attempt = db.Column(db.SmallInteger, default=0)
    staff = db.relationship('Staff', backref='user', uselist=False, lazy=False)

    def get_local_time(self):
        utc_time = datetime.utcnow().replace(tzinfo=pytz_utc)
        return utc_time.astimezone(timezone(self.company.timezone))

    def back_to_past(self):  # reset today time to 00:00:00
        local_time = self.get_local_time()
        return local_time.replace(hour=00, minute=00, second=00, microsecond=000000)




