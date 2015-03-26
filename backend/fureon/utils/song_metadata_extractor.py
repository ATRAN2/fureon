import subprocess
import mutagen

from fureon import config
from fureon.exceptions import FileNotFoundError, FileTypeError


class SongMetadataExtractor(object):
    SUPPORTED_FILE_TYPES = set(['audio/mp3', 'audio/vorbis', 'audio/x-flac'])
    ID3_TAG_TO_SONG_MODEL_MAP = {
        'TDRC' : 'date',
        'TCON' : 'genre',
        'TALB' : 'album',
        'TIT2' : 'title',
        'TPE1' : 'artist',
        'TRCK' : 'trackno',
    }
    VORBISCOMMENTS_TO_SONG_MODEL_MAP = {
        'date' : 'date',
        'genre' : 'genre',
        'album' : 'album',
        'title' : 'title',
        'artist' : 'artist',
        'tracknumber' : 'trackno',
    }

    def __init__(self):
        self.metadata = {}
        for metadata_entry in self.ID3_TAG_TO_SONG_MODEL_MAP.values():
            self.metadata[metadata_entry] = None
        self.metadata['picture_data'] = None

    def extract_metadata_from_song(self, song_path):
        song_data = self._get_and_validate_song_data(song_path)
        if 'audio/mp3' in song_data.mime:
            self._extract_id3_metadata(song_data)
        else:
            self._extract_vorbiscomments_metadata(song_data)
        self.metadata['duration'] = unicode(song_data.info.length)
        return self.metadata

    def _extract_id3_metadata(self, song_data):
        for id3_field, column_name in self.ID3_TAG_TO_SONG_MODEL_MAP.items():
            field_value = song_data[id3_field].text[0]
            self.metadata[column_name] = field_value
        self._format_id3_date_field()
        self._format_id3_trackno_field()
        if 'APIC:cover' in song_data:
            picture_data = song_data['APIC:cover'].data
            self.metadata['picture_data'] = picture_data

    def _extract_vorbiscomments_metadata(self, song_data):
        for vorbis_field, column_name in self.VORBISCOMMENTS_TO_SONG_MODEL_MAP.items():
            field_value = song_data[vorbis_field][0]
            self.metadata[column_name] = field_value
        picture_data = None
        if hasattr(song_data, 'pictures'):
            picture_data = song_data.pictures[0].data
        elif 'metadata_block_picture' in song_data:
            picture_data = song_data['metadata_block_picture'][0]
        self.metadata['picture_data'] = picture_data

    def _get_and_validate_song_data(self, song_path):
        try:
            song_data = mutagen.File(song_path)
        except IOError:
            raise FileNotFoundError(
                'File located at {0} was not found'.format(song_path)
            )
        if not song_data or not self._is_song_a_supported_filetype(song_data):
           raise FileTypeError(
               'Not a supported file type.  The song located at {0} is ' + \
               'is not one of the supported filetypes: {1}'\
               .format(song_path, str(self.SUPPORTED_FILE_TYPES))
           )
        return song_data

    def _format_id3_date_field(self):
        if self.metadata['date']:
            self.metadata['date'] = self.metadata['date'].text

    def _format_id3_trackno_field(self):
        # If Track Total field has a value, Track will be in the format
        # 'Track/Track Total.
        trackno_string = self.metadata['trackno']
        slash_index = trackno_string.find('/')
        if slash_index > 0:
            trackno_string = trackno_string[0:slash_index]
        self.metadata['trackno'] = trackno_string

    def _is_song_a_supported_filetype(self, song_data):
        for filetype_data in song_data.mime:
            if filetype_data in self.SUPPORTED_FILE_TYPES:
                return True
        return False
