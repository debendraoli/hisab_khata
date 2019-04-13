from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_mail import Mail
from flask_migrate import Migrate
from flask_wtf import CSRFProtect


db = SQLAlchemy()
bcrypt = Bcrypt()
mail = Mail()
migrate = Migrate()
csrf_protect = CSRFProtect()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'
