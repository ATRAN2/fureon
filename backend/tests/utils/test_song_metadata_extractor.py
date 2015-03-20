import os
import unittest
import subprocess

from fureon import config
from fureon.utils import song_metadata_extractor
from fureon.exceptions import FileNotFoundError
from tests import testing_utils


class TestSongMetadataExtractor(unittest.TestCase, testing_utils.CustomFileAssertions):
    @classmethod
    def setUpClass(cls):
        cls.extractor = song_metadata_extractor.SongMetadataExtractor()
        cls.test_song_path = os.path.join(
            config.PARENT_DIRECTORY, 'tests', 'test_files', 'test_song.mp3'
        )

    def test_extract_metadata_from_song(self):
        expected_metadata = {
            'year' : 2014,
            'genre' : 'test_genre',
            'album' : 'test_album',
            'title' : 'test_title',
            'artist' : 'test_artist',
            'duration' : 184,
            'trackno' : 1,
            'picture_format' : 'jpg',
        }
        self.assertEqual(
            expected_metadata,
            self.extractor.extract_metadata_from_song(self.test_song_path)
        )

    def test_extract_metadata_from_song_with_invalid_file(self):
        with self.assertRaises(FileNotFoundError):
            self.extractor.extract_metadata_from_song('/not/a/valid/song/path')

    def test_extract_art_from_song(self):
        test_file_directory = os.path.dirname(self.test_song_path)
        album_art = self.extractor.extract_art_from_song(self.test_song_path)
        art_file_path = os.path.join(testing_utils.TEST_TEMP_PATH, 'test_art.jpg')
        with open(art_file_path, 'wb') as image_out:
            image_out.write(album_art)
        self.assertIsImage(art_file_path)
        os.remove(art_file_path)
        self.assertFileDoesNotExist(art_file_path)

if __name__ == '__main__':
    unittest.main()
