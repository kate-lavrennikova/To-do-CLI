from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker, DeclarativeBase
from sqlalchemy.exc import OperationalError
from to_do_list.config import settings
from to_do_list.exceptions import DatabaseIsNotAvailableException



engine = create_engine(url=settings.database_url)
session_factory = sessionmaker(engine)

class Base(DeclarativeBase):
    pass

def db_init():
    try:
        Base.metadata.create_all(engine)
    except OperationalError:
        raise DatabaseIsNotAvailableException()
