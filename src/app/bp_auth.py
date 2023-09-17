from urllib.parse import urlsplit

from flask import (
    Blueprint,
    Response,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user, login_required, login_user, logout_user

from src.app import login_manager
from src.app.exceptions import (
    APIServiceUnavailableException,
    APIUnauthorizedException,
    UserCreateDuplicateException,
    UserCreateValuesException,
)
from src.app.forms import (
    ChangePasswordForm,
    LoginForm,
    RegistrationForm,
    ResetPasswordForm,
)
from src.app.models import Users
from src.app.services import UserService

auth = Blueprint('auth', __name__)


@login_manager.user_loader
def load_user(user_id: str) -> Users | None:
    return Users.get_by_id(user_id)


@auth.route('/login', methods=['GET', 'POST'])
def login() -> Response | str:
    """ login page """
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = LoginForm()
    if form.validate_on_submit():
        try:
            user: Users = UserService.login(
                identity=form.username.data,
                password=form.password.data,
            )
        except APIUnauthorizedException:
            flash(
                message='Login unsuccessful. Please check username and password.',
                category='danger',
            )
        except APIServiceUnavailableException:
            flash(
                message='Api service unavailable. Please try again later.',
                category='danger',
            )
        else:
            login_user(user, remember=False, force=True)
            flash(
                message='You have been logged in!',
                category='success',
            )

            next_url = request.args.get('next')
            if not next_url or urlsplit(next_url).netloc != '':
                return redirect(url_for('main.index'))

            return redirect(next_url)

    return render_template('login.html', title='Login', form=form)


@auth.route('/logout', methods=['GET', 'POST'])
def logout() -> Response | str:
    """ logout """
    logout_user()
    return redirect(url_for('main.index'))


@auth.route('/session', methods=['GET'])
@login_required
def session() -> Response | str:
    """ session information page """
    return render_template('session.html', title='Session', current_user=current_user)


@auth.route('/register', methods=['GET', 'POST'])
def register() -> Response | str:
    """ register page """
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = RegistrationForm()
    if form.validate_on_submit():
        # TODO регистрация через ручку
        try:
            UserService.register(
                username=form.username.data,
                email=form.email.data,
                password=form.password.data,
            )
        except UserCreateValuesException as e:
            flash(
                message="Can't register the user",
                category='danger',
            )
            if len(e.args) and type(e.args[0]) is dict:
                for field, message in e.args[0].items():
                    if field in form:
                        form[field].errors = message
        except UserCreateDuplicateException:
            flash(
                message='User already exists',
                category='danger',
            )
        else:
            flash(
                message='We are create new user now! Please log in.',
                category='info',
            )
            return redirect('/login')
    return render_template('register.html', form=form)


@auth.route('/reset', methods=['GET', 'POST'])
def reset() -> Response | str:
    """ reset password page """
    form = ResetPasswordForm()
    if form.validate_on_submit():
        # TODO: сброс пароля через ручку
        logout_user()
        return render_template('todo.html')
    return render_template('reset.html', form=form)


@auth.route('/change', methods=['GET', 'POST'])
def change() -> Response | str:
    """ change password page """
    form = ChangePasswordForm()
    if form.validate_on_submit():
        # TODO: смена пароля через ручку
        logout_user()
        return render_template('todo.html')
    return render_template('change.html', form=form)
