import os
import subprocess

import pytest
import mock

from fureon import config
from fureon.utils import song_metadata_extractor
from fureon.exceptions import FileNotFoundError, FileTypeError
from tests import testing_utils


class TestSongMetadataExtractor(testing_utils.CustomFileAssertions):
    def setup_method(self, method):
        self.extractor = song_metadata_extractor.SongMetadataExtractor()

    def test_extract_metadata_from_mp3(self):
        expected_metadata = {
            'date' : u'2014',
            'genre' : u'test_genre',
            'album' : u'test_album',
            'title' : u'test_title',
            'artist' : u'test_artist',
            'duration' : u'184.32',
            'trackno' : u'1',
        }
        song_path = os.path.join(
            testing_utils.TEST_FILES_PATH, 'test_song.mp3'
        )
        self._test_extract_metadata_from_song(
            expected_metadata, song_path, check_picture=True
        )

    def test_extract_metadata_from_flac(self):
        expected_metadata = {
            'date' : u'1969',
            'genre' : u'test_genre2',
            'album' : u'test_album2',
            'title' : u'test_title2',
            'artist' : u'test_artist2',
            'duration' : u'30.0',
            'trackno' : u'2',
        }
        song_path = os.path.join(
            testing_utils.TEST_FILES_PATH, 'more_songs', 'test_song2.flac'
        )
        self._test_extract_metadata_from_song(
            expected_metadata, song_path, check_picture=True
        )

    def test_extract_metadata_from_ogg(self):
        expected_metadata = {
            'date' : u'1980',
            'genre' : u'test_genre3',
            'album' : u'test_album3',
            'title' : u'test_title3',
            'artist' : u'test_artist3',
            'duration' : u'25.0006875',
            'trackno' : u'3',
        }
        song_path = os.path.join(
            testing_utils.TEST_FILES_PATH, 'more_songs', 'more_songs', 'test_song3.ogg'
        )
        self._test_extract_metadata_from_song(
            expected_metadata, song_path, check_picture=False
        )

    def _test_extract_metadata_from_song(self, expected_metadata, song_path, check_picture=True):
        with mock.patch.object(config, 'paths', testing_utils.MOCK_CONFIG_PATHS):
            song_metadata = self.extractor.extract_metadata_from_song(song_path)
        song_art = song_metadata.pop('picture_data')
        assert expected_metadata == song_metadata
        if check_picture:
            art_file_path = os.path.join(testing_utils.TEST_TEMP_PATH, 'test_art.jpg')
            with open(art_file_path, 'wb') as image_out:
                image_out.write(song_art)
            self.assertIsImage(art_file_path)
            os.remove(art_file_path)
            self.assertFileDoesNotExist(art_file_path)

    def test_extract_metadata_from_nonexistent_file(self):
        with pytest.raises(FileNotFoundError):
            self.extractor.extract_metadata_from_song('/not/a/valid/song/path')

    def test_extract_metadata_from_invalid_file_type(self):
        song_with_unsupported_filetype = os.path.join(
            testing_utils.TEST_FILES_PATH, 'more_songs', 'test_song4.mid'
        )
        with pytest.raises(FileTypeError):
            self.extractor.extract_metadata_from_song(song_with_unsupported_filetype)

if __name__ == '__main__':
    unittest.main()
