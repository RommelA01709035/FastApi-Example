import os
from collections.abc import Iterator
from datetime import datetime, timezone

from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL no está definida (connection string de Supabase)")
if DATABASE_URL.startswith(("postgres://", "postgresql://")):
    DATABASE_URL = "postgresql+psycopg://" + DATABASE_URL.split("://", 1)[1]

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True, 
    connect_args={
        "sslmode": "require",  
        "prepare_threshold": None, 
    },
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def now() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    @classmethod
    def get(cls, db: Session, id: int):
        return db.get(cls, id)

    @classmethod
    def list(cls, db: Session, limit: int = 10, offset: int = 0, **filters):
        query = select(cls).filter_by(**filters)
        total = db.scalar(select(func.count()).select_from(query.subquery()))
        rows = db.scalars(query.order_by(cls.id.desc()).limit(limit).offset(offset))
        return list(rows), total

    @classmethod
    def all(cls, db: Session, **filters):
        return list(db.scalars(select(cls).filter_by(**filters).order_by(cls.id.desc())))

    def save(self, db: Session):
        db.add(self)
        db.flush()
        return self


def get_db() -> Iterator[Session]:
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
