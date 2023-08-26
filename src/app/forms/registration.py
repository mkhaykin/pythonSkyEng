from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Regexp


class RegistrationForm(FlaskForm):
    username = StringField(
        label='Username',
        validators=[
            DataRequired(),
            Length(1, 64),
            Regexp(
                '^[A-Za-z][A-Za-z0-9_.]*$',
                0,
                'Usernames must have only letters, numbers, dots or underscores'
            )
        ],
        render_kw={
            'placeholder': 'Enter your username ...',
        },
    )

    email = StringField(
        label='Email',
        validators=[
            DataRequired(),
            Length(1, 64),
            Email(),
        ],
        render_kw={
            'placeholder': 'Enter your email ...',
        },
    )

    password = PasswordField(
        label='Password',
        validators=[
            DataRequired(),
            EqualTo('password2', message='Passwords must match.')
        ],
        render_kw={
            'placeholder': 'Enter password ...',
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
