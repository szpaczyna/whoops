import logging
import os
from collections import deque

from dynaconf import FlaskDynaconf
from flask import Flask

from src.utils import ImportStatus

from .whoop import WhoopClient

REQUIRED_VARS = [
    "CLIENT_ID",
    "CLIENT_SECRET",
    "REDIRECT_URI",
    "SQLALCHEMY_DATABASE_URI",
    "SECRET_KEY",
]


def create_app():
    for var in REQUIRED_VARS:
        if not os.getenv(var):
            raise EnvironmentError(f"Missing required environment variable: {var}")

    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
    )

    app = Flask(__name__)
    FlaskDynaconf(app)

    app.config["ImportQueue"] = deque()
    app.config["LastImportStatus"] = ImportStatus.NOT_STARTED

    app.config["WhoopClient"] = WhoopClient(
        os.getenv("CLIENT_ID", ""),
        os.getenv("CLIENT_SECRET", ""),
    )
    app.config["REDIRECT_URI"] = os.getenv("REDIRECT_URI")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("SQLALCHEMY_DATABASE_URI")

    # Ensure all models are registered before create_all() runs inside
    # load_extensions() (otherwise new tables like whoop_token are missing).
    from src.models import token as _token  # noqa: F401

    app.config.load_extensions()  # type: ignore

    # SECRET_KEY is required and must come from the environment, never from
    # settings.toml (which is committed).
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

    # Restore persisted Whoop tokens (if any) so restarts don't force re-auth.
    with app.app_context():
        try:
            from src.models.token import load_tokens

            load_tokens(app.config["WhoopClient"])
        except Exception:  # noqa: BLE001
            pass

    return app


if __name__ == "__main__":
    from waitress import serve

    serve(create_app(), host="0.0.0.0", port=5000)
