from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
from sqlalchemy.orm import sessionmaker

from fureon import config
from fureon.models.base import Base


Session = sessionmaker()

def connect_to_db():
    engine = create_db_engine()
    create_tables(engine)
    bind_session(engine)

def create_db_engine():
    return create_engine(URL(**get_database_config()))

def create_in_memory_engine():
    return create_engine('sqlite://')

def create_tables(engine):
    Base.metadata.create_all(engine)

def bind_session(engine):
    Session.configure(bind=engine)

def get_database_config():
    database_config = config.database
    for key, value in database_config.iteritems():
        if not value:
            database_config.pop(key)
    return database_config

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

