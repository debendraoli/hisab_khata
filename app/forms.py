from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, IntegerField, TextAreaField, PasswordField, SelectField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError
from wtforms.fields.html5 import EmailField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from . models import Supplier, Product, User, Company
from re import match


def get_dropdown_elements(model):
    try:
        data = model.query\
            .outerjoin(User, model.company_id == User.company_id).\
            filter(model.company_id == 1).all()
        return data
    except Exception:
        return {('', '')}


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Login')
    submit = SubmitField('Login')


class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    name = StringField('Full Name', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, max=32)])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password', message='Password do not match.')])
    company_code = StringField('Company Code', validators=[DataRequired()])

    submit = SubmitField('Register')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already exists.')

    def validate_company_code(self, company_code):
        company_code = Company.query.filter_by(code=company_code.data).first()
        if not company_code:
            raise ValidationError('Invalid company code.')


class ResetPassForm(FlaskForm):
    email = EmailField('Email address', validators=[DataRequired()])
    company_code = StringField('Company Code', validators=[DataRequired()])
    submit = SubmitField('Reset')


edit_product_form = '''
<form id="editProduct" action="">
                            <div class="form-group row mb-3">
                <div class="col-xl-4 mb-3">
                    <label class="form-control-label">Name<span class="text-danger ml-2">*</span></label>
                    <input id="product-name" type="text" value="" class="form-control">
                </div>
                <div class="col-xl-4 mb-5">
                    <label class="form-control-label">Color<span class="text-danger ml-2">*</span></label>
                    <input id="product-color" type="text" value="CA" class="form-control">
                </div>
                <div class="col-xl-4">
                    <label class="form-control-label">Size<span class="text-danger ml-2">*</span></label>
                    <input id="product-size" type="text" value="90045" class="form-control">
                </div>
            </div>

                            <div class="form-group row mb-3">
                <div class="col-xl-4 mb-3">
                    <label class="form-control-label">Price<span class="text-danger ml-2">*</span></label>
                    <input id="product-price" type="number" value="" class="form-control">
                </div>
                <div class="col-xl-4 mb-5">
                    <label class="form-control-label">Quantity<span class="text-danger ml-2">*</span></label>
                    <input id="product-quantity" type="number" value="" class="form-control">
                </div>
                <div class="col-xl-4">
                    <label class="form-control-label">Sold<span class="text-danger ml-2">*</span></label>
                    <input id="product-sold" type="number" value="" class="form-control">
                </div>
            </div>
<div class="form-group row mb-3">
<div class="col-xl-6 mb-3">
<label class="form-control-label">Code<span class="text-danger ml-2">*</span></label>
<input id="product-code" type="text" value="" class="form-control">
</div>
<div class="col-xl-6">
<label class="form-control-label">Supplier<span class="text-danger ml-2">*</span></label>
<select id="product-supplier" class="custom-select form-control">
    </select>

</div>
</div>
<div class="modal-footer">
<button type="button" class="btn btn-shadow" data-dismiss="modal">Close</button>
<button type="submit" class="btn btn-primary">Save</button>
</div>
</form>
'''


