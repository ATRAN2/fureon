import datetime

from fureon import db_operations
from fureon.models import stream_playlist
from tests import testing_utils

class TestPlaylist(object):
    def setup_method(self, method):
        testing_utils.connect_to_temporary_test_db()

    def teardown_method(self, method):
        testing_utils.empty_temp_directory()

    def test_add_song_by_id(self):
        with db_operations.session_scope() as session:
            playlist_manager = stream_playlist.PlaylistManager(session)
            playlist_manager.add_song_by_id(1)
            playlist_manager.add_song_by_id(2, True)
        expected_row_1 = {
            'id' : 1,
            'song_id' : 1,
            'user_requested' : False,
            'currently_playing' : False
        }
        expected_row_2 = {
            'id' : 2,
            'song_id' : 2,
            'user_requested' : True,
            'currently_playing' : False
        }
        with db_operations.session_scope() as session:
            playlist_manager = stream_playlist.PlaylistManager(session)
            playlist_song_1 = session.query(stream_playlist.Playlist).filter_by(id=1).first()
            playlist_song_2 = session.query(stream_playlist.Playlist).filter_by(id=2).first()
            playlist_song_1_contents = \
                playlist_manager.format_query_rows_to_dict(playlist_song_1)
            playlist_song_2_contents = \
                playlist_manager.format_query_rows_to_dict(playlist_song_2)
            playlist_song_1_time = playlist_song_1_contents.pop('datetime_added')
            playlist_song_2_time = playlist_song_2_contents.pop('datetime_added')

            assert expected_row_1 == playlist_song_1_contents
            assert type(datetime.datetime.now()) == type(playlist_song_1_time)
            assert expected_row_2 == playlist_song_2_contents
            assert type(datetime.datetime.now()) == type(playlist_song_2_time)

    def test_get_playlist_length(self):
        with db_operations.session_scope() as session:
            playlist_manager = stream_playlist.PlaylistManager(session)
            songs_to_add = 5
            for ii in range(songs_to_add):
                assert ii == playlist_manager.get_playlist_length()
                playlist_manager.add_song_by_id(ii)
            assert songs_to_add == playlist_manager.get_playlist_length()

    def test_set_first_song_as_currently_playing(self):
        with db_operations.session_scope() as session:
            playlist_manager = stream_playlist.PlaylistManager(session)
            playlist_manager.add_song_by_id(1)
            playlist_manager.set_first_song_as_currently_playing()
        with db_operations.session_scope() as session:
            first_song = session.query(stream_playlist.Playlist).filter_by(id=1).one()
            assert True == first_song.currently_playing

    def test_get_ordered_playlist_and_pop_first_song(self):
        with db_operations.session_scope() as session:
            playlist_manager = stream_playlist.PlaylistManager(session)
            playlist_manager.add_song_by_id(1)
            playlist_manager.add_song_by_id(2, True)
            playlist_manager.add_song_by_id(3)
            playlist_manager.add_song_by_id(4, True)
            ordered_playlist = playlist_manager.get_ordered_playlist()
            ordered_playlist_as_list = playlist_manager.get_ordered_playlist(as_list=True)
            assert type(list()) == type(ordered_playlist_as_list)
        expected_playlist = {}
        expected_song_ids = [2, 4, 1, 3]
        expected_requested_state = [True, True, False, False]
        for ii in range(len(expected_song_ids)):
            expected_playlist[ii] = {
                'song_id' : expected_song_ids[ii],
                'user_requested' : expected_requested_state[ii]
            }
        assert expected_playlist == ordered_playlist
        
        with db_operations.session_scope() as session:
            playlist_manager = stream_playlist.PlaylistManager(session)
            playlist_manager.pop_first_song()
            ordered_playlist = playlist_manager.get_ordered_playlist()
        expected_playlist = {}
        expected_song_ids.pop(0)
        expected_requested_state.pop(0)
        for ii in range(len(expected_song_ids)):
            expected_playlist[ii] = {
                'song_id' : expected_song_ids[ii],
                'user_requested' : expected_requested_state[ii]
            }
        assert expected_playlist == ordered_playlist


