import datetime

from sqlalchemy import Column, Integer, Boolean, DateTime

from fureon.models.base import Base, ModelManager


class Playlist(Base):
    __tablename__ = 'playlist'

    id = Column(Integer, primary_key=True)
    song_id = Column('song_id', Integer)
    datetime_added = Column('datetime_added', DateTime)
    user_requested = Column('user_requested', Boolean)
    currently_playing = Column('currently_playing', Boolean)

class PlaylistManager(ModelManager):
    def add_song_by_id(self, new_song_id, user_requested=False):
        new_playlist_song_data = {
            'song_id': new_song_id,
            'datetime_added': datetime.datetime.now(),
            'user_requested': user_requested,
            'currently_playing': False
        }
        new_playlist_song = Playlist(**new_playlist_song_data)
        self._session.add(new_playlist_song)

    def set_first_song_as_currently_playing(self):
        ordered_playlist_query = self._get_ordered_playlist_query()
        if not ordered_playlist_query:
            return False
        first_song = ordered_playlist_query[0]
        first_song.currently_playing = True
        return True

    def pop_first_song(self):
        ordered_playlist_query = self._get_ordered_playlist_query()
        if not ordered_playlist_query:
            return None
        first_song = ordered_playlist_query[0]
        self._session.delete(first_song)
        first_song = self.format_query_rows_to_dict([first_song])
        columns_to_remove = ['id', 'currently_playing']
        self.remove_columns_from_query_rows(columns_to_remove, first_song)
        return first_song[0]

    def get_playlist_length(self):
        return self._session.query(Playlist.id).count()

    def get_ordered_playlist(self, as_list=False):
        ordered_playlist = self._get_ordered_playlist_query()
        ordered_playlist = self.format_query_rows_to_dict(ordered_playlist)
        columns_to_remove = ['datetime_added', 'id', 'currently_playing']
        self.remove_columns_from_query_rows(columns_to_remove, ordered_playlist)
        if not as_list:
            ordered_playlist = self.format_list_to_numbered_dict(ordered_playlist)
        return ordered_playlist

    def _get_ordered_playlist_query(self):
        playlist = self._get_playlist()
        current_song = filter(lambda x: x.currently_playing == True, playlist)
        if current_song:
            current_song_index = playlist.index(current_song[0])
            playlist.pop(current_song_index)
        requested_songs = filter(lambda x: x.user_requested == True, playlist)
        requested_songs.sort(key=lambda x: x.datetime_added)
        unrequested_songs = filter(lambda x: x.user_requested == False, playlist)
        unrequested_songs.sort(key=lambda x: x.datetime_added)
        ordered_playlist_query = current_song + requested_songs + unrequested_songs
        return ordered_playlist_query

    def _get_playlist(self):
        return self._session.query(Playlist).all()

