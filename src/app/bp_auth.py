from urllib.parse import urlsplit

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from src.app import db, login_manager
from src.app.forms import (
    ChangePasswordForm,
    LoginForm,
    RegistrationForm,
    ResetPasswordForm,
)
from src.app.models import Users

auth = Blueprint('auth', __name__)


@login_manager.user_loader
def load_user(user_id: str) -> Users | None:
    return Users.get_by_id(user_id)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    """ login page """
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = LoginForm()
    if form.validate_on_submit():
        user: Users = Users.get_by_name(username=form.username.data)

        # если пользователя нет, то создаем пользователя
        if not user:
            user = Users(form.username.data)
            db.session.add(user)
            db.session.commit()

        # при входе _всегда_ запрашиваем токен (иначе надо отдельно проверять пароль или ловим уязвимость)
        user.request_token(password=form.password.data)

        if user.token:
            login_user(user, remember=False, force=True)
            flash(
                message='You have been logged in!',
                category='success',
            )

            next_url = request.args.get('next')
            if not next_url or urlsplit(next_url).netloc != '':
                return redirect(url_for('main.index'))

            return redirect(next_url)
        else:
            flash(
                message='Login Unsuccessful. Please check username and password',
                category='danger',
            )
            # TODO write log

    return render_template('login.html', title='Login', form=form)


@auth.route('/logout', methods=['GET', 'POST'])
def logout():
    """ logout """
    logout_user()
    return redirect(url_for('main.index'))


@auth.route('/session', methods=['GET'])
@login_required
def session():
    """ session information page """
    return render_template('session.html', title='Session', current_user=current_user)


@auth.route('/register', methods=['GET', 'POST'])
def register():
    """ register page """
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = RegistrationForm()
    if form.validate_on_submit():
        # TODO регистрация через ручку
        flash('We are create new user now! Please log in.')
        return render_template('todo.html')
    return render_template('register.html', form=form)


@auth.route('/reset', methods=['GET', 'POST'])
def reset():
    """ reset password page """
    form = ResetPasswordForm()
    if form.validate_on_submit():
        # TODO: сброс пароля через ручку
        logout_user()
        return render_template('todo.html')
    return render_template('reset.html', form=form)


@auth.route('/change', methods=['GET', 'POST'])
def change():
    """ change password page """
    form = ChangePasswordForm()
    if form.validate_on_submit():
        # TODO: смена пароля через ручку
        logout_user()
        return render_template('todo.html')
    return render_template('change.html', form=form)
