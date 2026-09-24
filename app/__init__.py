import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, render_template
from app.config import config_map
from app.extensions import bcrypt, csrf, cache, limiter


def create_app(config_name='development'):
    app = Flask(__name__)
    app.config.from_object(config_map[config_name])

    # Extensions
    bcrypt.init_app(app)
    csrf.init_app(app)
    cache.init_app(app)
    limiter.init_app(app)

    # Database (SQLite)
    from app import database
    database.init_app(app)

    # Blueprints
    register_blueprints(app)
    register_error_handlers(app)
    register_commands(app)
    setup_logging(app)

    return app


def register_blueprints(app):
    from app.routes.auth_routes import auth_bp
    from app.routes.dashboard_routes import dashboard_bp
    from app.routes.kontrak_routes import kontrak_bp
    from app.routes.user_routes import user_bp
    from app.routes.chart_routes import chart_bp
    from app.routes.export_routes import export_bp
    from app.routes.log_routes import log_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    app.register_blueprint(kontrak_bp, url_prefix='/kontrak')
    app.register_blueprint(user_bp, url_prefix='/users')
    app.register_blueprint(chart_bp, url_prefix='/api/chart')
    app.register_blueprint(export_bp, url_prefix='/export')
    app.register_blueprint(log_bp, url_prefix='/log')


def register_error_handlers(app):
    @app.errorhandler(404)
    def not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template('errors/500.html'), 500


def register_commands(app):
    from app.commands.create_admin import create_admin_command
    from app.commands.init_db import init_db_command
    from app.commands.sync_sheets import sync_sheets_command
    app.cli.add_command(create_admin_command)
    app.cli.add_command(init_db_command)
    app.cli.add_command(sync_sheets_command)


def setup_logging(app):
    if not app.debug:
        import os
        os.makedirs('logs', exist_ok=True)
        handler = RotatingFileHandler('logs/app.log', maxBytes=10_000_000, backupCount=5)
        handler.setFormatter(logging.Formatter(
            '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'))
        handler.setLevel(app.config['LOG_LEVEL'])
        app.logger.addHandler(handler)