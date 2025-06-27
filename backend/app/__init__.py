import os
from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base

Base = declarative_base()
_engine = None


def init_db(app: Flask) -> None:
    global _engine
    dsn = app.config.get("DATABASE_URL") or os.getenv(
        "DATABASE_URL", "sqlite:///demo.db"
    )
    _engine = create_engine(dsn, future=True, echo=False)
    Base.metadata.create_all(_engine)
    app.session = lambda: Session(_engine, autoflush=False)


def create_app() -> Flask:
    app = Flask(__name__, template_folder='../templates')
    app.config.from_mapping(
        SECRET_KEY=os.getenv("SECRET_KEY", "dev"),
        DATABASE_URL=os.getenv("DATABASE_URL", "sqlite:///demo.db"),
    )

    init_db(app)

    from .routes.items import bp as items_bp
    from .routes.pages import bp as pages_bp
    app.register_blueprint(items_bp)
    app.register_blueprint(pages_bp)

    return app
