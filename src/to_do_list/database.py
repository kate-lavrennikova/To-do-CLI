from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker, DeclarativeBase
from to_do_list.config import settings



engine = create_engine(url=settings.database_url)
session_factory = sessionmaker(engine)

class Base(DeclarativeBase):
    pass

def db_init():
    Base.metadata.create_all(engine)