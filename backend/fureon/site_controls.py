import os
import random

from fureon import db_operations, config
from fureon.utils import stream_player
from fureon.models import song, stream_playlist
from fureon.exceptions import DuplicateEntryError


class MainStreamControls(object):
    def __init__(self):
        self._database_controller = DatabaseControls()
        self._stream_player = stream_player.StreamPlayer()

    def add_random_song_to_playlist(self):
        with db_operations.session_scope() as session:
            random_song = song.get_random_song(session)
            self.add_song_with_user_request_to_playlist(
                random_song.id, user_requested=False
            )

    def add_song_with_user_request_to_playlist(self, song_id, user_requested=False):
        with db_operations.session_scope() as session:
            stream_playlist.add_song_by_id(session, song_id, user_requested)
        self._stream_player.add(song_id)


class DatabaseControls(object):
    SUPPORTED_FILE_TYPES = ('.mp3', '.ogg', '.flac')

    def update_song_db(self):
        song_directory = config.paths['song_directory']
        with db_operations.session_scope() as session:
            self._traverse_and_add_all_songs_in_directory(session, song_directory)

    def _traverse_and_add_all_songs_in_directory(self, session, song_directory):
        for root, dirs, files in os.walk(song_directory):
            for filename in files:
                if filename.endswith(self.SUPPORTED_FILE_TYPES):
                    song_path = os.path.join(root, filename)
                    try:
                        song.add_song_from_path(session, song_path)
                    except DuplicateEntryError:
                        pass

