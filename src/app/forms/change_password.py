from flask_wtf import FlaskForm
from wtforms import PasswordField, SubmitField
from wtforms.validators import DataRequired, EqualTo


class ChangePasswordForm(FlaskForm):
    password_old = PasswordField(
        label='Old password',
        validators=[
            DataRequired(),
        ],
        render_kw={
            'placeholder': 'Enter your old password ...',
        },

    )

    password = PasswordField(
        label='Password',
        validators=[
            DataRequired(),
            EqualTo('password2', message='Passwords must match.')
        ],
        render_kw={
            'placeholder': 'Enter your new password ...',
        },

    )
    password2 = PasswordField(
        label='Confirm password',
        validators=[
            DataRequired(),
        ],
        render_kw={
            'placeholder': 'Repeat password ...',
        },
    )
    submit = SubmitField('Register')
