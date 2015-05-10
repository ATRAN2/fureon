import os

from fureon import db_operations, config
from fureon.utils import stream_player, cache
from fureon.models import song, stream_playlist
from fureon.exceptions import DuplicateEntryError
from fureon.components.decorators import invalidate_cached_playlist
from fureon.components.stream_watcher import StreamPlayerWatcher


class MainStreamControls(object):
    def __init__(self, song_cache):
        if isinstance(song_cache, cache.SongCache):
            self._song_cache = song_cache
        else:
            raise TypeError('{0} requires a cache of {1}'.format(
                self.__class__.__name, type(cache.SongCache)
                )
            )
        self._database_controller = DatabaseControls()
        self._stream_player = stream_player.StreamPlayer()
        self._initialized = False

    def initialize_stream(self):
        self.load_song_library()
        self._stream_player.clear()
        self.add_random_songs_to_playlist_until_max_length()
        self.transition_to_next_song()
        stream_player_watcher = StreamPlayerWatcher.instance()
        stream_player_watcher.running = False
        stream_player_watcher.start()
        self._initialized = True

    def run_stream(self):
        if not self._initialized:
            self.initialize_stream
        self._stream_player.play()
        stream_player_watcher = StreamPlayerWatcher.instance()
        stream_player_watcher.running = True

    def load_song_library(self):
        self._stream_player.update()
        self._database_controller.update_song_db()

    def transition_to_next_song(self):
        with db_operations.session_scope() as session:
            playlist_manager = stream_playlist.PlaylistManager(session)
            song_manager = song.SongManager(session)
            playlist_manager.pop_first_song()
            playlist_manager.set_first_song_as_currently_playing()
            ordered_playlist = playlist_manager.get_ordered_playlist(as_list=True)
            next_two_songs = ordered_playlist[1:3]
            self._stream_player.crop()
            for coming_song in next_two_songs:
                song_data = song_manager.get_song_by_id(coming_song['song_id'])
                self._stream_player.add(song_data['file_path'])
        self.add_random_songs_to_playlist_until_max_length()

    def add_random_songs_to_playlist_until_max_length(self):
        with db_operations.session_scope() as session:
            playlist_manager = stream_playlist.PlaylistManager(session)
            max_playlist_size = config.stream_options['playlist_size']
            while playlist_manager.get_playlist_length() < max_playlist_size:
                self.add_random_song_with_user_request_to_playlist()

    def add_random_song_with_user_request_to_playlist(self, user_requested=False):
        with db_operations.session_scope() as session:
            song_manager = song.SongManager(session)
            random_song = self._get_random_unblocked_song(song_manager)
            self.add_song_with_user_request_to_playlist(
                random_song.id, user_requested
            )

    @invalidate_cached_playlist('_song_cache')
    def add_song_with_user_request_to_playlist(self, song_id, user_requested=False):
        with db_operations.session_scope() as session:
            playlist_maanger = stream_playlist.PlaylistManager(session)
            playlist_maanger.add_song_by_id(song_id, user_requested)
        if user_requested:
            self._song_cache.set_song_request_block_with_ttl(
                song_id, config.stream_options['song_request_cooldown']
            )

    def _get_random_unblocked_song(self, song_manager):
        max_attempts = 50
        attempts = 0
        random_song = None
        while not random_song:
            random_song = song_manager.get_random_song()
            if attempts >= max_attempts:
                break
            elif self._song_cache.get_song_block_ttl(random_song.id):
                random_song = None
                attempts += 1
        return random_song

class DatabaseControls(object):
    SUPPORTED_FILE_TYPES = ('.mp3', '.ogg', '.flac')

    def update_song_db(self):
        song_directory = config.paths['song_directory']
        with db_operations.session_scope() as session:
            song_manager = song.SongManager(session)
            self._traverse_and_add_all_songs_in_directory(song_manager, song_directory)

    def _traverse_and_add_all_songs_in_directory(self, song_manager, song_directory):
        for root, dirs, files in os.walk(song_directory):
            for filename in files:
                if filename.endswith(self.SUPPORTED_FILE_TYPES):
                    song_path = os.path.join(root, filename)
                    try:
                        song_manager.add_song_from_path(song_path)
                    except DuplicateEntryError:
                        pass

