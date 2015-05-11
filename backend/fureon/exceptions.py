from fureon.utils.logger import main_logger


class ExceptionWithLogger(Exception):
    def __init__(self, message, logger, level='warning'):
        super(ExceptionWithLogger, self).__init__(message)
        exception_name = self.__class__.__name__
        logger_message = u'{0}: {1}'.format(exception_name, message)
        logger_function = getattr(logger, level)
        logger_function(logger_message)

class FileNotFoundError(ExceptionWithLogger):
    def __init__(self, message='', logger=main_logger):
        super(FileNotFoundError, self).__init__(message, logger)

class FileTypeError(ExceptionWithLogger):
    def __init__(self, message='', logger=main_logger):
        super(FileTypeError, self).__init__(message, logger)

class DuplicateEntryError(ExceptionWithLogger):
    def __init__(self, message='', logger=main_logger, level='info'):
        super(DuplicateEntryError, self).__init__(message, logger, level)

