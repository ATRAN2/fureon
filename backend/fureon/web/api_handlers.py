from tornado.web import RequestHandler

from fureon import db_operations, constants
from fureon.components.cache_instances import song_cache
from fureon.models import stream_playlist, song


class APIRootHandler(RequestHandler):
    def get(self):
        endpoints = constants.ENDPOINT_DESCRIPTIONS
        self.write(endpoints)

class PlaylistSongsHandler(RequestHandler):
    def get(self):
        if song_cache.get_playlist():
            current_playlist = json.loads(song_cache.get_playlist())
        else:
            with db_operations.session_scope() as session:
                playlist_manager = stream_playlist.PlaylistManager(session)
                current_playlist = playlist_manager.get_ordered_playlist()
                song_manager = song.SongManager(session)
                for playlist_order, playlist_data in current_playlist.iteritems():
                    self._add_song_data_to_playlist_data(playlist_data, song_manager)
        self.write(current_playlist)

    def _add_song_data_to_playlist_data(self, playlist_data, song_manager):
        song = song_manager.get_song_by_id(playlist_data['song_id'])
        field_data_to_add = ['title', 'artist', 'duration']
        for field in field_data_to_add:
            playlist_data[field] = song[field]
