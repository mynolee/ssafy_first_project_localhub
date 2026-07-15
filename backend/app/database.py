from collections.abc import Generator

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import get_settings


class Base(DeclarativeBase):
    pass


database_url = get_settings().resolved_database_url
engine_options: dict = {}
if database_url.startswith("sqlite"):
    engine_options["connect_args"] = {"check_same_thread": False}
if database_url == "sqlite://":
    engine_options["poolclass"] = StaticPool

engine = create_engine(database_url, **engine_options)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def migrate_database_schema() -> None:
    """Apply the small additive migrations required by the local SQLite MVP."""
    inspector = inspect(engine)
    migrations = {
        "places": ("region", "ALTER TABLE places ADD COLUMN region VARCHAR(30) NOT NULL DEFAULT 'SEOUL'"),
        "posts": ("region", "ALTER TABLE posts ADD COLUMN region VARCHAR(30) NOT NULL DEFAULT 'SEOUL'"),
    }
    with engine.begin() as connection:
        for table_name, (column_name, statement) in migrations.items():
            if table_name not in inspector.get_table_names():
                continue
            columns = {column["name"] for column in inspector.get_columns(table_name)}
            if column_name not in columns:
                connection.execute(text(statement))


def get_db() -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
