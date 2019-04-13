from flask import request, redirect, url_for, jsonify, render_template
from flask_login import current_user, login_user, logout_user
from . import auth
from .. import bcrypt
from .models import User


@auth.route('/login/', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    if request.method == 'POST':
        email = request.json['email']
        password = request.json['pass']
        remember_me = True if request.json['remember_me'] else False
        user = User.query.filter_by(email=email, status=True).first()
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user, remember=remember_me)
            next_page = request.args.get('next', url_for('main.dashboard'))
            return jsonify({'success': True, 'message': 'Successful', 'redirect': next_page})
        return jsonify({'success': False, 'message': 'Invalid credentials.', 'redirect': False})
    return render_template('auth/login.html', title='Login')


@auth.route('/register/', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        '''hashed_pw = bcrypt.generate_password_hash(form.password.data)
        company = Company.query.filter_by(company_code=form.company_code.data).first()
        user = User(email=form.email.data, password=hashed_pw, company=company.id)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('auth.register.html', title='Register', form=form)'''


''''@app.route('/reset_pass/')
def reset_pass():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.company.id == current_user:
            msg = Message(
                "Password reset confirmation link for necomerce.online. ",
                recipients=[user.email]
            )
            mail.send(msg)
            flash(f'If {form.email.data} exists, email should be on the way.', 'success')
        return redirect(url_for('login'))
    return render_template('auth.reset_pass.html', title='Reset Pass')'''


@auth.route('/logout/')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
