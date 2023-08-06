from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.core.config import config

engine = create_engine(config.DATABASE_DSN, echo=True)


def get_session():
    return Session(engine)
