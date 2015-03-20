import os


APP_ROOT = os.path.dirname(os.path.abspath(__file__))
PARENT_DIRECTORY = os.path.normpath(APP_ROOT + os.sep + os.pardir)

# Set paths and database parameters prior to use
paths = {
    'metadata_extractor' : '' ,
    'mpd_db_root' : '', 
    'static_folder_path' : '', 
    }

database = {
    'drivername' : '',
    'host' : '',
    'port' : '',
    'username' : '',
    'password' : '',
    'database' : '',
}

