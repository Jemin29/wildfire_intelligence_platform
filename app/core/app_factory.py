from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, request

from app.api import register_blueprints
from app.core.config import get_config
from app.core.errors import register_error_handlers
from app.core.extensions import cors, db, jwt, migrate
from app.utils.logging_config import setup_logging


def create_app() -> Flask:
    root_dir = Path(__file__).resolve().parents[2]
    _load_environment(root_dir)

    app = Flask(
        __name__,
        template_folder=str(root_dir / "templates"),
        static_folder=str(root_dir / "static"),
        static_url_path="/static",
    )
    _configure_app(app)
    _configure_logging(app)
    _configure_extensions(app)
    _configure_blueprints(app)
    _configure_error_handlers(app)
    _register_startup_hooks(app)

    return app


def _load_environment(root_dir: Path) -> None:
    dotenv_path = root_dir / ".env"
    load_dotenv(dotenv_path, override=False)


def _configure_app(app: Flask) -> None:
    app.config.from_object(get_config())
    app.config.from_prefixed_env()
    app.url_map.strict_slashes = False


def _configure_logging(app: Flask) -> None:
    logger = setup_logging("wildfire_api")
    app.logger.handlers = logger.handlers
    app.logger.setLevel(logger.level)


def _configure_extensions(app: Flask) -> None:
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cors.init_app(
        app,
        resources={r"/api/*": {"origins": app.config["CORS_ORIGINS"]}},
    )
    _import_models()


def _configure_blueprints(app: Flask) -> None:
    register_blueprints(app)


def _configure_error_handlers(app: Flask) -> None:
    register_error_handlers(app)


def _register_startup_hooks(app: Flask) -> None:
    @app.before_request
    def _log_request_path() -> None:
        app.logger.debug("request_path=%s", request.path)
        if not app.config.get("_STARTUP_LOGGED", False):
            app.logger.info("wildfire_api_startup=ready")
            app.config["_STARTUP_LOGGED"] = True


def _import_models() -> None:
    from app import db as _db_module  # noqa: F401
