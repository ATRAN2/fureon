import unittest
import os
import datetime

from fureon import db_operations, config
from fureon.models import song
from fureon.web.api_handlers import convert_row_to_map
from tests import testing_utils


class TestSongModel(unittest.TestCase, testing_utils.CustomFileAssertions):
    def setUp(self):
        self.test_song_path = os.path.join(
            config.PARENT_DIRECTORY, 'tests', 'test_files', 'test_song.mp3'
        )
        testing_utils.connect_to_temporary_test_db()

    def test_add_new_song(self):
        art_path = os.path.join(testing_utils.TEST_TEMP_PATH, 'test_art.jpg')
        with db_operations.session_scope() as session:
            new_song_id = song.add_new_song(session, self.test_song_path, art_path)
        expected_row = {
            'id' : 1,
            'title' : u'test_title',
            'artist' : u'test_artist',
            'album' : u'test_album',
            'trackno' : u'1',
            'date' : u'2014',
            'genre' : u'test_genre',
            'duration' : u'184.32',
            'file_path' : unicode(self.test_song_path),
            'art_path' : unicode(art_path),
            'tags' : None,
            'play_count' : 0,
            'fave_count' : 0
        }
        with db_operations.session_scope() as session:
            added_song =  session.query(song.SongModel).filter_by(id=1).first()
            added_song_contents = convert_row_to_map(added_song)
            added_song_datetime = added_song_contents.pop('datetime_added')
            self.assertEqual(datetime.datetime, type(added_song_datetime))
            self.assertEqual(expected_row, added_song_contents)

    def tearDown(self):
        testing_utils.empty_temp_directory()

if __name__ == '__main__':
    unittest.main()
