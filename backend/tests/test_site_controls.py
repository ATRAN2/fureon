import unittest

from fureon import db_operations, config
from fureon.site_controls import DatabaseControls
from fureon.models import song
from tests import testing_utils


class TestDatabaseControls(unittest.TestCase):
    def setUp(self):
        self.test_songs_directory = os.path.join(
            config.PARENT_DIRECTORY, 'tests', 'test_files'
        )
        testing_utils.connect_to_temporary_test_db()

    def test_update_song_db(self):
        DatabaseControls.update_song_db()
        with db_operations.scope() as session:
            all_songs = session.query(song.SongModel).all()
            self.assertEqual(3, len(all_songs))

if __name__ == '__main__':
    unittest.main()
