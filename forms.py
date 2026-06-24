from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField, FloatField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional


class RegisterForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(1, 120)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(1, 160)])
    password = PasswordField('Password', validators=[DataRequired(), Length(6, 128)])
    confirm_password = PasswordField(
        'Confirm Password',
        validators=[DataRequired(), EqualTo('password', message="Passwords must match")]
    )
    submit = SubmitField('Register')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


class ServiceRequestForm(FlaskForm):
    device_type = SelectField(
        'Device Type',
        choices=[('TV', 'TV'), ('Fridge', 'Fridge'), ('Laptop', 'Laptop'), ('Other', 'Other')],
        validators=[DataRequired()]
    )
    brand = StringField('Brand', validators=[Optional(), Length(max=120)])
    model_no = StringField('Model No', validators=[Optional(), Length(max=120)])
    description = TextAreaField('Problem Description', validators=[DataRequired(), Length(max=2000)])
    submit = SubmitField('Submit Request')


class AssignEngineerForm(FlaskForm):
    engineer_id = SelectField('Assign Engineer', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Assign')


class ReceiptForm(FlaskForm):
    amount = FloatField('Amount', validators=[DataRequired()])
    payment_method = SelectField(
        'Payment Method',
        choices=[('cash', 'Cash'), ('card', 'Card'), ('upi', 'UPI')]
    )
    details = TextAreaField('Details', validators=[Optional()])
    submit = SubmitField('Generate Receipt')


# ======================
# NEW FORM: Engineer submits work done
# ======================
class WorkDoneForm(FlaskForm):
    work_done = TextAreaField('Work Description', validators=[DataRequired(), Length(max=2000)])
    submit = SubmitField('Submit Work')
