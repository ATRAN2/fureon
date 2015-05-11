import logging
import os

from fureon import config


if not config.paths['log_file']:
    log_path = os.path.join(config.PARENT_DIRECTORY, 'fureon.log')
else:
    log_path = config.paths['log_file']

main_logger = logging.getLogger('fureon')
main_logger.setLevel(logging.DEBUG)

fh = logging.FileHandler(log_path)
fh_verbosity = getattr(logging, config.logs['log_file_verbosity'], logging.INFO)
fh.setLevel(fh_verbosity)

ch = logging.StreamHandler()
ch_verbosity = getattr(logging, config.logs['console_verbosity'], logging.ERROR)
ch.setLevel(ch_verbosity)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)

main_logger.addHandler(fh)
main_logger.addHandler(ch)
