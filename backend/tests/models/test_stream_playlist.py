import datetime

from fureon import db_operations
from fureon.models import stream_playlist
from fureon.web.api_handlers import convert_row_to_map
from tests import testing_utils

class TestPlaylist(object):
    def setup_method(self, method):
        testing_utils.connect_to_temporary_test_db()

    def teardown_method(self, method):
        testing_utils.empty_temp_directory()

    def test_add_song_by_id(self):
        with db_operations.session_scope() as session:
            stream_playlist.add_song_by_id(session, 1)
            stream_playlist.add_song_by_id(session, 2, True)
        expected_row_1 = {
            'id' : 1,
            'song_id' : 1,
            'user_requested' : False
        }
        expected_row_2 = {
            'id' : 2,
            'song_id' : 2,
            'user_requested' : True
        }
        with db_operations.session_scope() as session:
            playlist_song_1 = session.query(stream_playlist.Playlist).filter_by(id=1).first()
            playlist_song_2 = session.query(stream_playlist.Playlist).filter_by(id=2).first()
            playlist_song_1_contents = convert_row_to_map(playlist_song_1)
            playlist_song_2_contents = convert_row_to_map(playlist_song_2)
            playlist_song_1_time = playlist_song_1_contents.pop('datetime_added')
            playlist_song_2_time = playlist_song_2_contents.pop('datetime_added')

            assert expected_row_1 == playlist_song_1_contents
            assert type(datetime.datetime.now()) == type(playlist_song_1_time)
            assert expected_row_2 == playlist_song_2_contents
            assert type(datetime.datetime.now()) == type(playlist_song_2_time)

