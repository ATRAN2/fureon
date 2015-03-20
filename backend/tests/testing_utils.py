import os
import subprocess
import unittest
import shutil

from fureon import config


TEST_TEMP_PATH = os.path.join(config.PARENT_DIRECTORY, 'tests', 'test_temp')

class CustomFileAssertions(object):
    def assertIsImage(self, image_path):
        image_check_proc = subprocess.Popen(
            [config.paths['metadata_extractor'], image_path],
            stderr = subprocess.STDOUT,
            stdout = subprocess.PIPE
        )
        is_image = False
        for line in iter(image_check_proc.stdout.readline, ''):
            if line.find('image/'):
                is_image = True
        if not is_image:
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

def empty_temp_directory():
    for file in os.listdir(TEST_TEMP_PATH):
        file_path = os.path.join(TEST_TEMP_PATH, file)
        if os.path.isfile(file_path):
            os.unlink(file_path)
        else:
            shutil.rmtree(file_path)
