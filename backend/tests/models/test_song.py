import os
import datetime

import mock

from fureon import db_operations, config
from fureon.models import song
from tests import testing_utils


class TestSongModel(testing_utils.CustomFileAssertions):
    @classmethod
    def setup_class(cls):
        cls.test_song_1_path = os.path.join(
            testing_utils.TEST_FILES_PATH, 'test_song.mp3')
        cls.test_song_2_path = os.path.join(
            testing_utils.TEST_FILES_PATH, 'more_songs', 'test_song2.flac')
        cls.test_song_3_path = os.path.join(
            testing_utils.TEST_FILES_PATH, 'more_songs', 'more_songs', 'test_song3.ogg')

    def setup_method(self, method):
        testing_utils.connect_to_temporary_test_db()

    def teardown_method(self, method):
        testing_utils.empty_temp_directory()

    def test_add_song_from_path_and_get_song_by_id(self):
        with mock.patch.object(config, 'paths', testing_utils.MOCK_CONFIG_PATHS):
            with db_operations.session_scope() as session:
                song_manager = song.SongManager(session)
                new_song_id = song_manager.add_song_from_path(self.test_song_1_path)
        file_uri = testing_utils.TEST_STATIC_URI + 'music/1.mp3'
        art_path = \
            os.path.join(testing_utils.TEST_TEMP_PATH, 'album-art', '1.jpg')
        art_uri = testing_utils.TEST_STATIC_URI + 'album-art/1.jpg'
        expected_row = {
            'id': 1,
            'title': u'test_title',
            'artist': u'test_artist',
            'album': u'test_album',
            'trackno': u'1',
            'date': u'2014',
            'genre': u'test_genre',
            'duration': u'184.32',
            'file_path': unicode(self.test_song_1_path),
            'file_uri': unicode(file_uri),
            'art_path': unicode(art_path),
            'art_uri': unicode(art_uri),
            'tags': None,
            'play_count': 0,
            'fave_count': 0,
        }
        with db_operations.session_scope() as session:
            song_manager = song.SongManager(session)
            added_song = song_manager.get_song_by_id(new_song_id)
            added_song_datetime = added_song.pop('datetime_added')
            assert datetime.datetime == type(added_song_datetime)
            assert expected_row == added_song
        self.assertIsImage(art_path)

    def test_get_artist_by_name(self):
        with mock.patch.object(config, 'paths', testing_utils.MOCK_CONFIG_PATHS):
            with db_operations.session_scope() as session:
                song_manager = song.SongManager(session)
                song_manager.add_song_from_path(self.test_song_1_path)
                artist_name = 'test_artist'
                artist_data = song_manager.get_artist_by_name(artist_name)
        expected_artist_data = {
            u'0': {
                'title': u'test_title',
                'id': 1,
                'trackno': u'1',
                'date': u'2014',
                'album': u'test_album',
                'fave_count': 0,
                'play_count': 0
            }
        }
        assert expected_artist_data == artist_data

    def test_get_album_by_name(self):
        with mock.patch.object(config, 'paths', testing_utils.MOCK_CONFIG_PATHS):
            with db_operations.session_scope() as session:
                song_manager = song.SongManager(session)
                song_manager.add_song_from_path(self.test_song_1_path)
                album_name = 'test_album'
                album_data = song_manager.get_album_by_name(album_name)
        art_uri = testing_utils.TEST_STATIC_URI + 'album-art/1.jpg'
        expected_album_data = {
            u'0': {
                'title': u'test_title',
                'artist': u'test_artist',
                'id': 1,
                'trackno': u'1',
                'date': u'2014',
                'art_uri': unicode(art_uri),
                'fave_count': 0,
                'play_count': 0
            }
        }
        assert expected_album_data == album_data

    def test_get_song_count(self):
        test_song_paths = [
            self.test_song_1_path, self.test_song_2_path, self.test_song_3_path
        ]
        expected_song_counts = [1, 2, 3]
        with mock.patch.object(config, 'paths', testing_utils.MOCK_CONFIG_PATHS):
            map(
                self._add_song_and_check_song_count,
                test_song_paths, expected_song_counts
            )

    @testing_utils.retry_test_n_times(3)
    def test_get_random_song(self):
        test_song_paths = [
            self.test_song_1_path, self.test_song_2_path, self.test_song_3_path
        ]
        with mock.patch.object(config, 'paths', testing_utils.MOCK_CONFIG_PATHS):
            with db_operations.session_scope() as session:
                song_manager = song.SongManager(session)
                for test_song_path in test_song_paths:
                    song_manager.add_song_from_path(test_song_path)
        song_access_count = {1: 0, 2: 0, 3: 0}
        total_random_queries = 50
        with db_operations.session_scope() as session:
            song_manager = song.SongManager(session)
            for random_query in range(total_random_queries):
                random_song = song_manager.get_random_song()
                song_access_count[random_song.id] += 1
        query_count_threshold = total_random_queries//len(song_access_count)//1.4
        for song_id, access_count in song_access_count.iteritems():
            assert access_count >= query_count_threshold

    def _add_song_and_check_song_count(self, song_path, expected_song_count):
        with db_operations.session_scope() as session:
            song_manager = song.SongManager(session)
            assert expected_song_count-1 == song_manager.get_song_count()
        with db_operations.session_scope() as session:
            song_manager = song.SongManager(session)
            song_manager.add_song_from_path(song_path)
        with db_operations.session_scope() as session:
            song_manager = song.SongManager(session)
            assert expected_song_count == song_manager.get_song_count()
