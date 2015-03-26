import os


APP_ROOT = os.path.dirname(os.path.abspath(__file__))
PARENT_DIRECTORY = os.path.normpath(APP_ROOT + os.sep + os.pardir)

# Set paths and database parameters prior to use
paths = {
    'mpd_db_root' : '',
    'static_folder_path' : '',
    'log_file' : os.path.join(PARENT_DIRECTORY, 'fureon.log')
    }

database = {
    'drivername' : '',
    'host' : '',
    'port' : '',
    'username' : '',
    'password' : '',
    'database' : '',
}

# Set log verbosity. Verbosity in ascending order:
# CRITICAL, ERROR, WARNING, INFO, DEBUG
logs = {
    'console_verbosity' : 'ERROR',
    'log_file_verbosity' : 'INFO',
}
