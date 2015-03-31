import mock

from fureon import db_operations, config, site_controls
from fureon.models import stream_playlist, song
from fureon.utils import stream_player
from tests import testing_utils


class TestMainStreamControls(object):
    @classmethod
    def setup_class(cls):
        cls._stream_controller = site_controls.MainStreamControls()

    def setup_method(self, method):
        testing_utils.connect_to_temporary_test_db()
        with mock.patch.object(config, 'paths', testing_utils.MOCK_CONFIG_PATHS):
            self._stream_controller._database_controller.update_song_db()

    def teardown_method(self, method):
        testing_utils.empty_temp_directory()

#    def test_load_song_library(self):
#        self._stream_controller.load_song_library()

    @mock.patch('fureon.utils.stream_player.StreamPlayer.add')
    def test_add_song_with_user_request_to_playlist(self, mock_stream_player_add):
        with db_operations.session_scope() as session:
            test_songs = session.query(song.Song).all()
            self._stream_controller.add_song_with_user_request_to_playlist(
                test_songs[0].id, user_requested=False
            )
            assert 1 == session.query(stream_playlist.Playlist.id).count()
            self._stream_controller.add_song_with_user_request_to_playlist(
                test_songs[1].id, user_requested=True
            )
            assert 2 == session.query(stream_playlist.Playlist.id).count()

            first_song = session.query(stream_playlist.Playlist).filter_by(id=1).one()
            assert False == first_song.user_requested
            second_song = session.query(stream_playlist.Playlist).filter_by(id=2).one()
            assert True == second_song.user_requested
        assert True == mock_stream_player_add.called

    @mock.patch('fureon.utils.stream_player.StreamPlayer.add')
    def test_add_random_song_to_playlist(self, mock_stream_player_add):
        self._stream_controller.add_random_song_to_playlist()
        with db_operations.session_scope() as session:
            assert 1 == session.query(stream_playlist.Playlist).count()
        assert True == mock_stream_player_add.called

class TestDatabaseControls(object):
    @classmethod
    def setup_class(cls):
        cls._database_controller = site_controls.DatabaseControls()

    def setup_method(self, method):
        testing_utils.connect_to_temporary_test_db()

    def teardown_method(self, method):
        testing_utils.empty_temp_directory()

    def test_update_song_db(self):
        with mock.patch.object(config, 'paths', testing_utils.MOCK_CONFIG_PATHS):
            self._database_controller.update_song_db()
        with db_operations.session_scope() as session:
            all_songs = session.query(song.Song).all()
            assert 3 == len(all_songs)

if __name__ == '__main__':
    unittest.main()
