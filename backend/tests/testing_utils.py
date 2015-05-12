import os
import shutil
import imghdr

import fakeredis
import mock

from fureon import config, db_operations, site_controls
from fureon.utils import cache


TEST_TEMP_PATH = os.path.join(config.PARENT_DIRECTORY, 'tests', 'test_temp')
TEST_FILES_PATH = os.path.join(config.PARENT_DIRECTORY, 'tests', 'test_files')
TEST_STATIC_URI = 'http://my.testurl.com/stuff/'
TEST_STREAM_ENDPOINT = 'http://my.streamendpoint.com:1234/swag.ogg'

def create_mock_cache_from_class(cache_class):
    with mock.patch('fureon.utils.cache.redis.StrictRedis', fakeredis.FakeStrictRedis):
        mock_cache = cache_class(host='notahost', port=1234, db=0)
        return mock_cache

TEST_SONG_CACHE = create_mock_cache_from_class(cache.SongCache)
# TEST_USER_CACHE = create_mock_cache_from_class(cache.UserCache)

MOCK_CONFIG_PATHS = {
    'song_directory': TEST_FILES_PATH,
    'static_folder_path': TEST_TEMP_PATH,
    'static_uri': TEST_STATIC_URI,
    'stream_endpoint': TEST_STREAM_ENDPOINT,
    'log_file': TEST_TEMP_PATH,
}

class CustomFileAssertions(object):
    def assertIsImage(self, image_path):
        if not imghdr.what(image_path):
            raise AssertionError('File in path is not an image: {0}'.format(image_path))

    def assertFileExists(self, path):
        if not self._file_exists(path):
            raise AssertionError('File in path does not exist: {0}'.format(path))

    def assertFileDoesNotExist(self, path):
        if self._file_exists(path):
            raise AssertionError('File in path does exists: {0}'.format(path))

    def _file_exists(self, path):
        if os.path.isfile(path):
            return True
        else:
            return False

class TestingWithDBBaseClass(object):
    @classmethod
    def setup_class(cls):
        cls._song_cache = TEST_SONG_CACHE
        cls._stream_controller = site_controls.MainStreamControls(cls._song_cache)

    def setup_method(self, method):
        connect_to_temporary_test_db()
        with mock.patch.object(config, 'paths', MOCK_CONFIG_PATHS):
            self._stream_controller._database_controller.update_song_db()

    def teardown_method(self, method):
        self._song_cache.flush_db()
        empty_temp_directory()

def connect_to_temporary_test_db():
    engine = db_operations.create_in_memory_engine()
    db_operations.create_tables(engine)
    db_operations.bind_session(engine)

def empty_temp_directory():
    for file in os.listdir(TEST_TEMP_PATH):
        file_path = os.path.join(TEST_TEMP_PATH, file)
        if os.path.isfile(file_path):
            os.unlink(file_path)
        else:
            shutil.rmtree(file_path)

class retry_test_n_times(object):
    def __init__(self, retry_attempts):
        self._retry_attempts = retry_attempts

    def __call__(self, func):
        def wrapped_func(*args, **kwargs):
            current_attempt_count = 0
            while True:
                try:
                    return_values = func(*args, **kwargs)
                    break
                except AssertionError:
                    current_attempt_count += 1
                    if current_attempt_count >= self._retry_attempts:
                        raise
                    test_class = args[0]
                    self._run_teardown_and_setup_methods(test_class)
            return return_values
        return wrapped_func

    def _run_teardown_and_setup_methods(self, test_class):
        if hasattr(test_class, 'teardown_method'):
            teardown_method = getattr(test_class, 'teardown_method')
            teardown_method(None)
        if hasattr(test_class, 'setup_method'):
            setup_method = getattr(test_class, 'setup_method')
            setup_method(None)

