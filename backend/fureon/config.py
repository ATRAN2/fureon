import os


APP_ROOT = os.path.dirname(os.path.abspath(__file__))
PARENT_DIRECTORY = os.path.normpath(APP_ROOT + os.sep + os.pardir)
TIME_FORMAT = '%Y-%m-%d %H-%M-%S'

SECRET_KEY = os.urandom(64) # change this to a long, randomly-generated string if you want to be able to persist user tokens across server restarts

# Set paths and database parameters prior to use
paths = {
    'song_directory' : '',
    'static_folder_path' : '',
    'static_uri' : '',
    'stream_endpoint' : '',
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

# Redis cache connection parameters
cache = {
    'host' : 'localhost',
    'port' : 6379,
}

# Request cooldown in minutes
stream_options = {
    'song_request_cooldown' : 60,
    'playlist_size' : 20
}

# Set log verbosity. Verbosity in ascending order:
# CRITICAL, ERROR, WARNING, INFO, DEBUG
logs = {
    'console_verbosity' : 'ERROR',
    'log_file_verbosity' : 'INFO',
}

# IPs that can continuously add requests to songs
# without waiting for request cooldown
request_ip_whitelist = set([
])
