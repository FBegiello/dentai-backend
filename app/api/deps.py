from typing import Generator

from sqlalchemy.orm import Session

from app.db import db_session


def get_db() -> Generator[Session, None, None]:
    with db_session() as db:
        yield db
