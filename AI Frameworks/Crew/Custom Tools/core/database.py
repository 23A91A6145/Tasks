"""Database engine, session factory and declarative base."""

from datetime import datetime, timezone

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from .config import settings


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _connect_args() -> dict:
    if settings.DATABASE_URL.startswith("sqlite"):
        return {"check_same_thread": False}
    return {}


engine = create_engine(settings.DATABASE_URL, connect_args=_connect_args())
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Create tables for development. Use Alembic migrations in production."""
    from app import models  # noqa: F401  (register models on Base)

    Base.metadata.create_all(bind=engine)
    _ensure_columns()


# Lightweight, idempotent schema upgrades for the SQLite dev database so an
# existing dev.db keeps working after new nullable columns are added to a
# model. (Postgres deployments use the Alembic migrations instead.)
_SCHEMA_UPGRADES = {
    "users": [
        ("password_reset_token", "VARCHAR(255)"),
        ("password_reset_expires_at", "DATETIME"),
    ],
}


def _ensure_columns() -> None:
    if not settings.DATABASE_URL.startswith("sqlite"):
        return
    from sqlalchemy import inspect, text

    try:
        with engine.begin() as conn:
            inspector = inspect(conn)
            for table, columns in _SCHEMA_UPGRADES.items():
                if table not in inspector.get_table_names():
                    continue
                existing = {col["name"] for col in inspector.get_columns(table)}
                for name, ddl_type in columns:
                    if name not in existing:
                        conn.execute(text(f'ALTER TABLE "{table}" ADD COLUMN {name} {ddl_type}'))
    except Exception as exc:  # pragma: no cover
        import logging

        logging.getLogger("tenantdesk.db").warning("Schema upgrade skipped: %s", exc)
