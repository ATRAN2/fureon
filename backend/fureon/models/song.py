import os
import datetime
import logging
import imghdr
import errno
import random
from urlparse import urljoin

from sqlalchemy import Column, Integer, String, DateTime

from fureon import config
from fureon.exceptions import DuplicateEntryError
from fureon.utils.song_metadata_extractor import SongMetadataExtractor
from fureon.models.base import Base, ModelManager


module_logger = logging.getLogger(__name__)

class Song(Base):
    __tablename__ = 'song'

    id = Column(Integer, primary_key=True)
    title = Column('title', String)
    artist = Column('artist', String)
    album = Column('album', String, nullable=True)
    trackno = Column('trackno', String, nullable=True)
    date = Column('date', String, nullable=True)
    genre = Column('genre', String, nullable=True)
    duration = Column('duration', String)
    file_path = Column('file_path', String)
    file_uri = Column('file_uri', String)
    art_path = Column('art_path', String, nullable=True)
    art_uri = Column('art_uri', String, nullable=True)
    datetime_added = Column('datetime_added', DateTime)
    tags = Column('tags', String, nullable=True)
    play_count = Column('play_count', Integer, default=0)
    fave_count = Column('fave_count', Integer, default=0)

class SongManager(ModelManager):
    def add_song_from_path(self, song_path):
        song_path = unicode(song_path, 'utf-8')
        self._check_for_duplicate_song_entry(song_path)
        extractor = SongMetadataExtractor()
        metadata = extractor.extract_metadata_from_song(song_path)
        picture_data = metadata.pop('picture_data')
        new_song = Song(**metadata)
        self._session.add(new_song)
        self._session.flush()
        art_path = None
        art_uri = None
        if picture_data:
            picture_extension = \
                self._get_picture_extension_from_picture_data(picture_data)
            art_path, art_uri = \
                self._get_art_path_and_uri(str(new_song.id), picture_extension)
            self._save_album_art_to_file(picture_data, art_path)
        new_song.datetime_added = datetime.datetime.now()
        new_song.file_path = song_path
        new_song.file_uri = self._create_and_return_song_uri_link(str(new_song.id), song_path)
        new_song.art_path = unicode(art_path)
        new_song.art_uri = unicode(art_uri)
        return new_song.id

    def get_song_by_id(self, song_id):
        song = self._session.query(Song).filter_by(id=song_id).one()
        return self.format_query_rows_to_dict(song)

    def get_artist_by_name(self, artist_name):
        artist_songs = self._session.query(Song).filter_by(artist=artist_name).all()
        artist_songs = self.format_query_rows_to_dict(artist_songs)
        columns_to_remove = \
            ['genre', 'duration', 'file_path', 'file_uri', 'datetime_added',
             'tags', 'artist', 'art_path', 'art_uri']
        self.remove_columns_from_query_rows(columns_to_remove, artist_songs)
        artist_songs = self.format_list_to_numbered_dict(artist_songs)
        return artist_songs

    def get_album_by_name(self, album_name):
        album_songs = self._session.query(Song).filter_by(album=album_name).all()
        album_songs = self.format_query_rows_to_dict(album_songs)
        columns_to_remove = \
            ['genre', 'duration', 'file_path', 'file_uri', 'datetime_added',
             'tags', 'album', 'art_path']
        self.remove_columns_from_query_rows(columns_to_remove, album_songs)
        album_songs = self.format_list_to_numbered_dict(album_songs)
        return album_songs

    def get_song_count(self):
        return self._session.query(Song.id).count()

    def get_random_song(self):
        song_count = self.get_song_count()
        random_row_number = random.randint(0, song_count-1)
        return self._session.query(Song).slice(random_row_number,random_row_number+1).one()

    def _save_album_art_to_file(self, picture_data, art_path):
        art_directory = os.path.dirname(art_path)
        self._create_directory(art_directory)
        with open(art_path, 'wb') as image_out:
            image_out.write(picture_data)

    def _get_picture_extension_from_picture_data(self, picture_data):
        picture_format = imghdr.what(None, picture_data)
        extension = None
        if picture_format == 'jpeg':
            extension = 'jpg'
        elif picture_format == 'png':
            extension = 'png'
        return extension

    def _get_art_path_and_uri(self, file_name, picture_format):
        static_folder_path = config.paths['static_folder_path']
        if not static_folder_path:
            return ['', '']
        art_file_name = '{0}.{1}'.format(file_name, picture_format)
        art_path = os.path.join(static_folder_path, 'album-art', art_file_name)
        art_uri = urljoin(
            config.paths['static_uri'], 'album-art/{0}'.format(art_file_name)
        )
        return art_path, art_uri

    def _create_and_return_song_uri_link(self, song_id, song_path):
        song_extension = os.path.splitext(song_path)[1]
        link_path = os.path.join( config.paths['static_folder_path'], 'music',
            '{0}{1}'.format(song_id, song_extension)
        )
        link_directory = os.path.dirname(link_path)
        self._create_directory(link_directory)
        self._create_sym_link(song_path, link_path)
        song_uri = urljoin(
            config.paths['static_uri'], 'music/{0}{1}'.format(song_id, song_extension)
        )
        return song_uri

    def _create_directory(self, directory_path):
        try:
            os.makedirs(directory_path)
        except OSError as e:
            if e.errno == errno.EEXIST:
                pass
            else:
                raise

    def _create_sym_link(self, source_path, link_path):
        try:
            os.symlink(source_path, link_path)
        except OSError as e:
            if e.errno == errno.EEXIST:
                os.remove(link_path)
                os.symlink(source_path, link_path)

    def _does_song_exist(self, song_path):
        if self._session.query(Song).filter_by(file_path=song_path).count():
            return True
        else:
            return False

    def _check_for_duplicate_song_entry(self, song_path):
        if self._does_song_exist(song_path):
            error_message = u'The song located at {0} is already in the database'
            raise DuplicateEntryError(
                message=error_message.format(song_path),
                logger=module_logger,
                level='info'
            )
