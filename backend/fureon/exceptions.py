import logging


logging.basicConfig(level=100)

class FileNotFoundError(Exception):
    def __init__(self, message):
        super(FileNotFoundError, self).__init__(message)
        logging.warning('FileNotFoundError {0}'.format(message))
        pass

class FileTypeError(Exception):
    def __init__(self, message):
        super(FileTypeError, self).__init__(message)
        logging.warning('FileTypeError {0}'.format(message))
        self.message = message
        pass

