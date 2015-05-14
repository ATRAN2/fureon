import mutagen
import logging

from fureon.exceptions import FileNotFoundError, FileTypeError


module_logger = logging.getLogger(__name__)


class SongMetadataExtractor(object):
    SUPPORTED_FILE_TYPES = set(['audio/mp3', 'audio/vorbis', 'audio/x-flac'])
    ID3_TAG_TO_SONG_MODEL_MAP = {
        'TDRC': 'date',
        'TCON': 'genre',
        'TALB': 'album',
        'TIT2': 'title',
        'TPE1': 'artist',
        'TRCK': 'trackno',
    }
    VORBISCOMMENTS_TO_SONG_MODEL_MAP = {
        'date': 'date',
        'genre': 'genre',
        'album': 'album',
        'title': 'title',
        'artist': 'artist',
        'tracknumber': 'trackno',
    }

    def __init__(self):
        self._metadata = {}
        for metadata_entry in self.ID3_TAG_TO_SONG_MODEL_MAP.values():
            self._metadata[metadata_entry] = None
        self._metadata['picture_data'] = None

    def extract_metadata_from_song(self, song_path):
        song_data = self._get_and_validate_song_data(song_path)
        if 'audio/mp3' in song_data.mime:
            self._extract_id3_metadata(song_data)
        else:
            self._extract_vorbiscomments_metadata(song_data)
        self._metadata['duration'] = unicode(song_data.info.length)
        return self._metadata

    def _extract_id3_metadata(self, song_data):
        for id3_field, column_name in self.ID3_TAG_TO_SONG_MODEL_MAP.items():
            if song_data.get(id3_field):
                field_value = song_data.get(id3_field).text[0]
            else:
                field_value = ''
            self._metadata[column_name] = field_value
        self._format_id3_date_field()
        self._format_id3_trackno_field()
        picture_data = None
        if 'APIC:cover' in song_data:
            picture_data = song_data['APIC:cover'].data
        elif 'APIC:' in song_data:
            picture_data = song_data['APIC:'].data
        self._metadata['picture_data'] = picture_data

    def _extract_vorbiscomments_metadata(self, song_data):
        for vorbis_field, column_name in self.VORBISCOMMENTS_TO_SONG_MODEL_MAP.items():
            if song_data.get(vorbis_field):
                field_value = song_data[vorbis_field][0]
            else:
                field_value = ''
            self._metadata[column_name] = field_value
        picture_data = None
        if hasattr(song_data, 'pictures') and song_data.pictures:
            picture_data = song_data.pictures[0].data
        elif 'metadata_block_picture' in song_data:
            picture_data = song_data['metadata_block_picture'][0]
        self._metadata['picture_data'] = picture_data

    def _get_and_validate_song_data(self, song_path):
        try:
            song_data = mutagen.File(song_path)
        except IOError:
            error_message = 'File located at {0} was not found'
            raise FileNotFoundError(
                message=error_message.format(song_path),
                logger=module_logger
            )
        if not song_data or not self._is_song_a_supported_filetype(song_data):
            error_message = 'The song located at {0} is not one ' +\
                'of the supported music mime types: {1}'
            raise FileTypeError(
                message=error_message.format(song_path, str(self.SUPPORTED_FILE_TYPES)),
                logger=module_logger
            )
        return song_data

    def _format_id3_date_field(self):
        if self._metadata['date']:
            self._metadata['date'] = self._metadata['date'].text

    def _format_id3_trackno_field(self):
        # If Track Total field has a value, Track will be in the format
        # 'Track/Track Total.
        trackno_string = self._metadata['trackno']
        slash_index = trackno_string.find('/')
        if slash_index > 0:
            trackno_string = trackno_string[0:slash_index]
        self._metadata['trackno'] = trackno_string

    def _is_song_a_supported_filetype(self, song_data):
        for filetype_data in song_data.mime:
            if filetype_data in self.SUPPORTED_FILE_TYPES:
                return True
        return False
