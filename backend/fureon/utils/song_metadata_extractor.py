import subprocess

from afkradio import config
from afkradio.exceptions import FileNotFoundError, FileTypeError


class SongMetadataExtractor(object):
    SUPPORTED_FILE_TYPES = ('MP3', 'OGG', 'FLAC')
    EXIFTOOL_FIELD_TO_SONG_MODEL_MAP = {
        'Year' : 'year',
        'Genre' : 'genre',
        'Album' : 'album',
        'Title' : 'title',
        'Artist' : 'artist',
        'Duration' : 'duration',
        'Track' : 'trackno',
    }

    def extract_metadata_from_song(self, song_path):
        metadata = self._initialize_metadata()
        extractor_proc = subprocess.Popen(
            [config.paths['metadata_extractor'], song_path],
            stderr = subprocess.STDOUT,
            stdout = subprocess.PIPE
        )
        for line in iter(extractor_proc.stdout.readline, ''):
            self._validate_extractor_output(line, song_path)
            self._parse_extractor_output_into_metadata(line, metadata)
        self._format_metadata(metadata)
        return metadata

    @classmethod
    def extract_art_from_song(cls, song_path):
        save_image_proc = subprocess.Popen(
            [config.paths['metadata_extractor'], '-picture', '-b', song_path],
            stdout = subprocess.PIPE
        )
        album_art_image = save_image_proc.stdout.read()
        return album_art_image

    def _initialize_metadata(self):
        metadata = {}
        for metadata_entry in self.EXIFTOOL_FIELD_TO_SONG_MODEL_MAP.values():
            metadata[metadata_entry] = None
        metadata['picture_format'] = None
        return metadata

    def _validate_extractor_output(self, line, song_path):
        if line.startswith('File not found'):
            print line
            raise FileNotFoundError('File not found: {0}'.format(song_path))
        elif line.startswith('File Type'):
            file_type = self._get_field_value_from_extractor_output(line)
            if file_type not in self.SUPPORTED_FILE_TYPES:
                raise FileTypeError(
                    'Not a supported file type.  The song located at {0} is ' + \
                    'a(n) {1} which is not within the supported filetypes {2}'\
                    .format(song_path, file_type, str(SUPPORTED_FILE_TYPES))
                )

    def _parse_extractor_output_into_metadata(self, line, metadata):
        extractor_field_name = self._get_field_name_from_extractor_output(line)
        if extractor_field_name in self.EXIFTOOL_FIELD_TO_SONG_MODEL_MAP:
            model_field_name = \
                self.EXIFTOOL_FIELD_TO_SONG_MODEL_MAP[extractor_field_name]
            field_value = self._get_field_value_from_extractor_output(line)
            metadata[model_field_name] = field_value
        if extractor_field_name == 'Picture Mime Type':
            picture_format = self._get_picture_format(line)
            if picture_format:
                metadata['picture_format'] = picture_format

    def _get_field_value_from_extractor_output(self, line):
        colon_index = line.find(':')
        return line[(colon_index+2):-1]

    def _get_field_name_from_extractor_output(self, line):
        field_name_end_index = line.find('  ')
        return line[0:field_name_end_index]

    def _get_picture_format(self, line):
        field_value = self._get_field_value_from_extractor_output(line)
        picture_format = None
        if field_value == 'image/png':
            picture_format = 'png'
        elif field_value == 'image/jpg' or field_value == 'image/jpeg':
            picture_format = 'jpg'
        return picture_format

    def _format_metadata(self, metadata):
        if metadata['year']:
            metadata['year'] = int(metadata['year'])
        if metadata['duration']:
            self._format_duration(metadata)
        if metadata['trackno']:
            self._format_trackno(metadata)

    def _format_duration(self, metadata):
        # Slice from [0:7] since sometimes duration_string is formatted
        # as 'H:MM:SS (approx)'
        duration_string = metadata['duration'][0:7]
        hours, minutes, seconds = duration_string.split(':')
        duration_in_seconds = int(hours)*3600 + int(minutes)*60 + int(seconds)
        metadata['duration'] = duration_in_seconds

    def _format_trackno(self, metadata):
        # If Track Total field has a value, Track will be in the format
        # 'Track/Track Total.
        trackno_string = metadata['trackno']
        slash_index = trackno_string.find('/')
        if slash_index > 0:
            trackno_string = trackno_string[0:slash_index]
        metadata['trackno'] = int(trackno_string)
