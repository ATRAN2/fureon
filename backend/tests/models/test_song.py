import unittest
import os
import datetime

from fureon import db_operations, config
from fureon.models import song
from fureon.web.api_handlers import convert_row_to_map
from tests import testing_utils


class TestSongModel(unittest.TestCase, testing_utils.CustomFileAssertions):
    def setUp(cls):
        cls.test_song_path = os.path.join(
            config.PARENT_DIRECTORY, 'tests', 'test_files', 'test_song.mp3'
        )
        engine = db_operations.connect_to_in_memory_db()
        db_operations.create_tables(engine)
        db_operations.bind_session(engine)

    def test_add_new_song(self):
        art_path = os.path.join(testing_utils.TEST_TEMP_PATH, 'test_art.jpg')
        with db_operations.session_scope() as session:
            new_song_id = song.add_new_song(session, self.test_song_path, art_path)
        expected_row = {
            'id' : 1,
            'title' : u'test_title',
            'artist' : u'test_artist',
            'album' : u'test_album',
            'trackno' : 1,
            'year' : 2014,
            'genre' : u'test_genre',
            'duration' : 184,
            'file_path' : unicode(self.test_song_path),
            'art_path' : unicode(art_path),
            'extra' : None,
            'play_count' : 0,
            'fave_count' : 0
        }
        with db_operations.session_scope() as session:
            added_song =  session.query(song.SongModel).filter_by(id=1).first()
            added_song_contents = convert_row_to_map(added_song)
            self.maxDiff = None
            datetime_added = added_song_contents.pop('datetime_added')
            self.assertEqual(datetime.datetime, type(datetime_added))
            self.assertEqual(expected_row, added_song_contents)

    def tearDown(self):
        testing_utils.empty_temp_directory()

if __name__ == '__main__':
    unittest.main()
