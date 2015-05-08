import mock

from fureon import db_operations, config, site_controls
from fureon.models import stream_playlist, song
from fureon.utils import stream_player, cache
from tests import testing_utils


class TestMainStreamControls(testing_utils.TestingWithDBBaseClass):
    @mock.patch('fureon.utils.stream_player.StreamPlayer.update')
    def test_load_song_library(self, mock_stream_player_update):
        with mock.patch.object(config, 'paths', testing_utils.MOCK_CONFIG_PATHS):
            self._stream_controller.load_song_library()
            with db_operations.session_scope() as session:
                song_manager = song.SongManager(session)
                assert 3 == song_manager.get_song_count()
        assert True == mock_stream_player_update.called

    def test_add_song_with_user_request_to_playlist(self):
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

    def test_add_random_song_with_user_request_to_playlist(self):
        self._stream_controller.add_random_song_with_user_request_to_playlist()
        with db_operations.session_scope() as session:
            assert 1 == session.query(stream_playlist.Playlist).count()

    def test_add_random_songs_to_playlist_until_max_length(self):
        with db_operations.session_scope() as session:
            playlist_manager = stream_playlist.PlaylistManager(session)
            assert 0 == playlist_manager.get_playlist_length()
            self._stream_controller.add_random_songs_to_playlist_until_max_length()
            playlist_size = config.stream_options['playlist_size']
            assert playlist_size == playlist_manager.get_playlist_length()

    @mock.patch('fureon.utils.stream_player.StreamPlayer.crop')
    @mock.patch('fureon.utils.stream_player.StreamPlayer.add')
    def test_transition_to_next_song(self, mock_add, mock_crop):
        with db_operations.session_scope() as session:
            playlist_manager = stream_playlist.PlaylistManager(session)
            prev_playlist = playlist_manager.get_ordered_playlist()
            self._stream_controller.transition_to_next_song()
            after_playlist = playlist_manager.get_ordered_playlist()
            assert prev_playlist != after_playlist
            self._stream_controller.transition_to_next_song()
        assert True == mock_add.called
        assert True == mock_crop.called

    @mock.patch('fureon.components.stream_watcher.StreamPlayerWatcher.run')
    @mock.patch('fureon.utils.stream_player.StreamPlayer.add')
    @mock.patch('fureon.utils.stream_player.StreamPlayer.crop')
    @mock.patch('fureon.utils.stream_player.StreamPlayer.clear')
    @mock.patch('fureon.utils.stream_player.StreamPlayer.update')
    def test_initialize_stream(self, mock_update, mock_clear, mock_crop,  mock_add, mock_run):
        with mock.patch.object(config, 'paths', testing_utils.MOCK_CONFIG_PATHS):
            self._stream_controller.initialize_stream()
        assert True == mock_update.called
        assert True == mock_clear.called
        assert True == mock_crop.called
        assert True == mock_add.called
        assert True == mock_run.called
#
#    @mock.patch('fureon.utils.stream_player.StreamPlayer.play')
#    def test_run_stream(self, mock_play):
#        self._stream_controller.run_stream()
#        assert True == mock_play.called

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
