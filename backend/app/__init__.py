import os
from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from .db import Base                 # declarative_base() – один источник
from .models_auth import User, Role   # модели можно импортировать здесь

_engine = None      # переменная-хранилище движка — нужна в нескольких местах


# ---------------------------------------------------------------------------
#  Инициализация базы: движок, таблицы, пользователь admin
# ---------------------------------------------------------------------------
def init_db(app: Flask) -> None:
    global _engine

    dsn = app.config.get("DATABASE_URL") or os.getenv(
        "DATABASE_URL", "sqlite:///demo.db"
    )
    _engine = create_engine(dsn, future=True, echo=False)

    # Создаём таблицы, если их ещё нет
    Base.metadata.create_all(_engine)

    # Первый пользователь admin (создаётся один раз)
    with Session(_engine) as s:
        if not s.query(User).first():
            admin = User(
                email="admin@example.com",
                password=User.hash_pwd("admin"),
            )
            admin.roles.append(Role(name="admin"))
            s.add(admin)
            s.commit()

    # Удобная фабрика сессий, чтобы другие модули могли делать current_app.session()
    app.session = lambda: Session(_engine, autoflush=False)


# ---------------------------------------------------------------------------
#  Фабрика Flask-приложения
# ---------------------------------------------------------------------------
def create_app() -> Flask:
    app = Flask(__name__, template_folder="../templates")
    app.config.from_mapping(
        SECRET_KEY=os.getenv("SECRET_KEY", "dev"),
        DATABASE_URL=os.getenv("DATABASE_URL", "sqlite:///demo.db"),
    )

    # База + данные по-умолчанию
    init_db(app)

    # --- Blueprints с CRUD и страницами ---
    from .routes.items import bp as items_bp
    from .routes.pages import bp as pages_bp
    app.register_blueprint(items_bp)
    app.register_blueprint(pages_bp)

    # --- Авторизация ---
    from .auth import bp as auth_bp, login_mgr
    app.register_blueprint(auth_bp)   # /login  /logout
    login_mgr.init_app(app)           # включает Flask-Login

    return app
