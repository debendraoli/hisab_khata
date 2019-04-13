from flask import Flask
from extensions import db, bcrypt, mail, migrate, csrf_protect, login_manager
from .main.routes import main
from .auth.routes import auth
from .sale.routes import sale
from .people.routes import people
from .setting.routes import setting
from .transaction.routes import transaction
from .inventory.routes import inventory
from .report.routes import report
from .people.models import Company


def create_app():
    app = Flask(__name__)
    app.config.from_object('config')
    db.init_app(app)
    bcrypt.init_app(app)
    migrate.init_app(app, db)
    csrf_protect.init_app(app)
    login_manager.init_app(app)
    app.register_blueprint(main)
    app.register_blueprint(auth)
    app.register_blueprint(sale)
    app.register_blueprint(people)
    app.register_blueprint(setting)
    app.register_blueprint(transaction)
    app.register_blueprint(inventory)
    app.register_blueprint(report)

    return app





