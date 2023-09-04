from logging.config import dictConfig

from flask import Flask, render_template
from flask_login import LoginManager, logout_user
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData

metadata = MetaData(
    naming_convention={
        'ix': 'ix_%(column_0_label)s',
        'uq': 'uq_%(table_name)s_%(column_0_name)s',
        'ck': 'ck_%(table_name)s_%(constraint_name)s',
        'fk': 'fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s',
        'pk': 'pk_%(table_name)s'
    }
)

dictConfig({
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
        'full': {
            'format': '%(asctime)s [%(levelname)s] '
                      '- APP: %(name)s '
                      '- MODULE: %(module)s '
                      '- FUNCTION: %(funcName)s '
                      '- LINE: %(lineno)d : %(message)s',
        },
    },

    'handlers': {
        'wsgi': {
            'class': 'logging.StreamHandler',
            'stream': 'ext://flask.logging.wsgi_errors_stream',
            'formatter': 'full',
        },
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
            'level': 'INFO',
            'stream': 'ext://sys.stdout'
        },
    },
    'loggers': {
        'root': {
            'handlers': [
                'console',
                # 'wsgi',
            ],
            'level': 'INFO',
            'propagate': False,
        },
    }
})

login_manager: LoginManager = LoginManager()
db: SQLAlchemy = SQLAlchemy(metadata=metadata)
migrate: Migrate = Migrate()


def create_app() -> Flask:
    app: Flask = Flask(
        __name__,
        template_folder='templates',
        static_folder='static',
    )

    app.config['SECRET_KEY'] = 'secret-key-goes-here'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite'

    login_manager.session_protection = 'strong'
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'
    login_manager.refresh_view = 'auth.login'
    login_manager.needs_refresh_message = 'need to refresh'
    login_manager.init_app(app)

    db.init_app(app)

    migrate.init_app(app, db, render_as_batch=True)

    # blueprint for auth routes
    from .bp_auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    # blueprint for non-auth parts of app
    from .bp_main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    @app.before_request
    def response_processor2():
        from flask import flash
        from flask_login import current_user

        from .models import Users

        user: Users = current_user
        if isinstance(user, Users):
            if user.is_token_expired():
                flash(message='Your session is expired.', category='info')
                logout_user()
            elif user.is_token_needs_updating():
                user.refresh_token()
        return None

    @app.errorhandler(404)
    def not_found_error(error):
        # TODO write log
        return render_template('404.html', error=error), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        # TODO write log
        return render_template('500.html', error=error), 500

    @app.errorhandler(503)
    def service_unavailable(error):
        db.session.rollback()
        # TODO write log
        return render_template('503.html', error=error), 503

    return app


if __name__ == '__main__':
    create_app().run()
