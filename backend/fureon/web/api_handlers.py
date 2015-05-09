import json

from tornado import ioloop
from tornado.web import RequestHandler

from fureon import db_operations, constants, config
from fureon.models import stream_playlist, song
from fureon.components.cache_instances import song_cache


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
            song_cache.set_playlist(json.dumps(current_playlist))
        self.write(current_playlist)

    def _add_song_data_to_playlist_data(self, playlist_data, song_manager):
        song = song_manager.get_song_by_id(playlist_data['song_id'])
        field_data_to_add = ['title', 'artist', 'duration']
        for field in field_data_to_add:
            playlist_data[field] = song[field]

class FindSongByIDHandler(RequestHandler):
    def get(self):
        song_id = self.request.arguments['song-id'][0]
        with db_operations.session_scope() as session:
            song_manager = song.SongManager(session)
            song_data = song_manager.get_song_by_id(song_id)
            song_data['datetime_added'] = \
                song_data['datetime_added'].strftime(config.TIME_FORMAT)
        self.write(song_data)

class RequestSongByIDHandler(RequestHandler):
    def __init__(self, *args, **kwargs):
        super(RequestSongByIDHandler, self).__init__(*args, **kwargs)
        from fureon.app import main_stream_controller
        self._stream_controller = main_stream_controller

    def post(self):
        song_id = self.request.arguments['song-id'][0]
        self._stream_controller.add_song_with_user_request_to_playlist(
            song_id, user_requested=True
        )

class FindAlbumByNameHandler(RequestHandler):
    def get(self):
        album_name = self.request.arguments['name'][0]
        with db_operations.session_scope() as session:
            song_manager = song.SongManager(session)
            album_data = song_manager.get_album_by_name(album_name)
        self.write(album_data)

class FindArtistByNameHandler(RequestHandler):
    def get(self):
        artist_name = self.request.arguments['name'][0]
        with db_operations.session_scope() as session:
            song_manager = song.SongManager(session)
            artist_name = song_manager.get_artist_by_name(artist_name)
        self.write(artist_name)

class GetStreamEndpointHandler(RequestHandler):
    def get(self):
        stream_endpoint = {
            'stream_endpoint' : config.paths['stream_endpoint']
        }
        self.write(stream_endpoint)
