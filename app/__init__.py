"""Application factory."""

from __future__ import annotations

from flask import Flask, render_template

from .config import BaseConfig, get_config
from .extensions import csrf, db, login_manager


def create_app(config_class: type[BaseConfig] | None = None) -> Flask:
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object(config_class or get_config())

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    _register_user_loader()
    _register_blueprints(app)
    _register_error_handlers(app)
    _register_cli(app)

    return app


def _register_user_loader() -> None:
    from .models.user import User

    @login_manager.user_loader
    def load_user(user_id: str) -> User | None:
        return db.session.get(User, int(user_id))


def _register_blueprints(app: Flask) -> None:
    from .blueprints.auth import auth_bp
    from .blueprints.clients import clients_bp
    from .blueprints.dumpsters import dumpsters_bp
    from .blueprints.main import main_bp
    from .blueprints.rentals import rentals_bp
    from .blueprints.reports import reports_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(clients_bp, url_prefix="/clients")
    app.register_blueprint(dumpsters_bp, url_prefix="/dumpsters")
    app.register_blueprint(rentals_bp, url_prefix="/rentals")
    app.register_blueprint(reports_bp, url_prefix="/reports")


def _register_error_handlers(app: Flask) -> None:
    @app.errorhandler(404)
    def not_found(_error):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def server_error(_error):
        return render_template("errors/500.html"), 500


def _register_cli(app: Flask) -> None:
    @app.cli.command("init-db")
    def init_db() -> None:
        """Create all database tables."""
        db.create_all()
        print("Database initialized.")
