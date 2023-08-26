from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Email


class ResetPasswordForm(FlaskForm):
    email = StringField(
        label='Email',
        validators=[
            DataRequired(),
            Email(),
        ],
        render_kw={
            'placeholder': 'Enter your email ...',
        }
    )
    submit = SubmitField('Request Password Reset')
