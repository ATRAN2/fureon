from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
from sqlalchemy.orm import sessionmaker

from fureon import config
from fureon.models import song
from fureon.models.base import Base


Session = sessionmaker()

def connect_to_db():
    return create_engine(URL(**config.database))

def connect_to_in_memory_db():
    return create_engine('sqlite://')

def create_tables(engine):
    Base.metadata.create_all(engine)

def bind_session(engine):
    Session.configure(bind=engine)

@contextmanager
def session_scope():
    session = Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()

