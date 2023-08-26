from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    username = StringField(
        label='Username',
        validators=[
            DataRequired(),
        ],
        render_kw={
            'placeholder': 'Enter your username or email ...',
        },
    )

    password = PasswordField(
        label='Password',
        validators=[
            DataRequired()
        ],
        render_kw={
            'placeholder': 'Enter your password ...',
        },

    )

    submit = SubmitField('Login')
