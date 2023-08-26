# from flask_wtf import FlaskForm
# from wtforms import PasswordField, StringField, SubmitField
# from wtforms.validators import (
#     DataRequired,
#     Email,
#     EqualTo,
#     Length,
#     Regexp,
#     ValidationError,
# )


# def validate_email(field):
#     # TODO не использовать, проверка в ручке
#     if Users.query.filter_by(email=field.data.lower()).first():
#         raise ValidationError('Email already registered.')
#
#
# def validate_username(field):
#     # TODO не использовать, проверка в ручке
#     if Users.query.filter_by(username=field.data).first():
#         raise ValidationError('Username already in use.')
