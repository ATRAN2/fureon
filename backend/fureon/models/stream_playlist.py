from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base

import config
from fureon.models.base import Base


class Playlist(Base):
    __tablename__ = 'playlist'

    id = Column(Integer, primary_key=True)
    song_id = Column(Integer)
    add_time = Column(DateTime)
    user_requested = Column(Boolean, default=False)


