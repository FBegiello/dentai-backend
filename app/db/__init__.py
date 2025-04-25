from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import as_declarative
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings

engine = create_engine(
    settings.DATABASE_URI, pool_pre_ping=True, pool_size=5, echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@contextmanager
def db_session() -> Generator[Session, None, None]:
    try:
        db: Session = SessionLocal()
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
