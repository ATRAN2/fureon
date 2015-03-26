from fureon import config
from fureon.utils.logger import main_logger


class FileNotFoundError(Exception):
    def __init__(self, message='', logger=main_logger):
        super(FileNotFoundError, self).__init__(message)
        logger.warning('FileNotFoundError: {0}'.format(message))

class FileTypeError(Exception):
    def __init__(self, message='', logger=main_logger):
        super(FileTypeError, self).__init__(message)
        logger.warning('FileTypeError: {0}'.format(message))
        self.message = message
