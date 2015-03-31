import datetime

from sqlalchemy import Column, Integer, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base

from fureon import config
from fureon.models.base import Base


class Playlist(Base):
    __tablename__ = 'playlist'

    id = Column(Integer, primary_key=True)
    song_id = Column('song_id', Integer)
    datetime_added = Column('datetime_added', DateTime)
    user_requested = Column('user_requested', Boolean)

def add_song_by_id(session, new_song_id, user_requested=False):
    new_playlist_song_data = {
        'song_id' : new_song_id,
        'datetime_added' : datetime.datetime.now(),
        'user_requested' : user_requested
    }
    new_playlist_song = Playlist(**new_playlist_song_data)
    session.add(new_playlist_song)

