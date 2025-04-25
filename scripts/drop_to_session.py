from sqlalchemy.orm import Session

from app.core.config import settings  # noqa
from app.db import SessionLocal

db: Session = SessionLocal()

# run with python -i
