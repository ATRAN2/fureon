import os
import subprocess
import unittest
import shutil
import imghdr

from fureon import config, db_operations


TEST_TEMP_PATH = os.path.join(config.PARENT_DIRECTORY, 'tests', 'test_temp')
TEST_FILES_PATH = os.path.join(config.PARENT_DIRECTORY, 'tests', 'test_files')

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

def connect_to_temporary_test_db():
    engine = db_operations.connect_to_in_memory_db()
    db_operations.create_tables(engine)
    db_operations.bind_session(engine)

def empty_temp_directory():
    for file in os.listdir(TEST_TEMP_PATH):
        file_path = os.path.join(TEST_TEMP_PATH, file)
        if os.path.isfile(file_path):
            os.unlink(file_path)
        else:
            shutil.rmtree(file_path)
