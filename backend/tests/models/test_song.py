import os
import datetime

import mock

from fureon import db_operations, config
from fureon.models import song
from fureon.web.api_handlers import convert_row_to_map
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

    def test_add_song_from_path(self):
        with mock.patch.object(config, 'paths', testing_utils.MOCK_CONFIG_PATHS):
            with db_operations.session_scope() as session:
                new_song_id = song.add_song_from_path(session, self.test_song_1_path)
        art_path = \
            os.path.join(testing_utils.TEST_TEMP_PATH, 'album-art', '1.jpg')
        expected_row = {
            'id' : 1,
            'title' : u'test_title',
            'artist' : u'test_artist',
            'album' : u'test_album',
            'trackno' : u'1',
            'date' : u'2014',
            'genre' : u'test_genre',
            'duration' : u'184.32',
            'file_path' : unicode(self.test_song_1_path),
            'art_path' : unicode(art_path),
            'tags' : None,
            'play_count' : 0,
            'fave_count' : 0
        }
        with db_operations.session_scope() as session:
            added_song =  session.query(song.Song).filter_by(id=1).first()
            added_song_contents = convert_row_to_map(added_song)
            added_song_datetime = added_song_contents.pop('datetime_added')
            assert datetime.datetime == type(added_song_datetime)
            assert expected_row == added_song_contents
        self.assertIsImage(art_path)

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

    def test_get_random_song(self):
        test_song_paths = [
            self.test_song_1_path, self.test_song_2_path, self.test_song_3_path
        ]
        with mock.patch.object(config, 'paths', testing_utils.MOCK_CONFIG_PATHS):
            with db_operations.session_scope() as session:
                for test_song_path in test_song_paths:
                    song.add_song_from_path(session, test_song_path)
        song_access_count = {1:0, 2:0, 3:0}
        total_random_queries = 50
        with db_operations.session_scope() as session:
            for random_query in range(total_random_queries):
                random_song = song.get_random_song(session)
                song_access_count[random_song.id] += 1
        query_count_threshold = total_random_queries//len(song_access_count)//1.3
        for song_id, access_count in song_access_count.iteritems():
            assert access_count >= query_count_threshold

    def _add_song_and_check_song_count(self, song_path, expected_song_count):
        with db_operations.session_scope() as session:
            assert expected_song_count-1 == song.get_song_count(session)
        with db_operations.session_scope() as session:
            song.add_song_from_path(session, song_path)
        with db_operations.session_scope() as session:
            assert expected_song_count == song.get_song_count(session)


if __name__ == '__main__':
    unittest.main()
