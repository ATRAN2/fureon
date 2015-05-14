import json
from urllib import urlencode

import mock
import tornado
from tornado.testing import AsyncHTTPTestCase

from fureon import db_operations, constants, config
from fureon.models import song
from fureon.app import api_endpoints
from tests import testing_utils


class TestAPIHandlers(AsyncHTTPTestCase, testing_utils.TestingWithDBBaseClass):
    def get_app(self):
        app = tornado.web.Application(
            api_endpoints,
        )
        return app

    def test_api_root(self):
        response = self._fetch_response_data_from_url('/api')
        assert response.code == 200
        expected_json = constants.ENDPOINT_DESCRIPTIONS
        assert expected_json == json.loads(response.body)

    def test_playlist_query(self):
        number_of_songs_to_add = 5
        for ii in range(number_of_songs_to_add):
            self._stream_controller.add_random_song_with_user_request_to_playlist()
        with mock.patch('fureon.web.api_handlers.song_cache', testing_utils.TEST_SONG_CACHE):
            response = self._fetch_response_data_from_url('/api/playlist')
        assert response.code == 200
        json_data = json.loads(response.body)
        assert number_of_songs_to_add == len(json_data)
        playlist_song_fields = [
            'song_id', 'title', 'artist', 'user_requested', 'duration'
        ]
        for field in playlist_song_fields:
            assert field in json_data['1']

    def test_find_song_by_id(self):
        song_id = 1
        url = '/api/song/find?song-id={0}'.format(song_id)
        response = self._fetch_response_data_from_url(url)
        assert response.code == 200
        json_data = json.loads(response.body)
        with db_operations.session_scope() as session:
            song_manager = song.SongManager(session)
            expected_data = song_manager.get_song_by_id(song_id)
            expected_data['datetime_added'] = \
                expected_data['datetime_added'].strftime(config.TIME_FORMAT)
        assert expected_data == json_data

    @mock.patch('fureon.site_controls.MainStreamControls.add_song_with_user_request_to_playlist')
    def test_request_song_by_id(self, mock_song_request):
        song_id = '1'
        url = '/api/request_song'
        post_data = {'song-id': song_id}
        response = self._post_data_to_url(url, post_data)
        assert response.code == 200
        assert mock_song_request.called

    def test_find_album_by_name(self):
        album_name = 'test_album'
        url = '/api/album/find?name={0}'.format(album_name)
        response = self._fetch_response_data_from_url(url)
        assert response.code == 200
        json_data = json.loads(response.body)
        with db_operations.session_scope() as session:
            song_manager = song.SongManager(session)
            expected_data = song_manager.get_album_by_name(album_name)
        assert expected_data == json_data

    def test_find_artist_by_name(self):
        artist_name = 'test_artist'
        url = '/api/artist/find?name={0}'.format(artist_name)
        response = self._fetch_response_data_from_url(url)
        assert response.code == 200
        json_data = json.loads(response.body)
        with db_operations.session_scope() as session:
            song_manager = song.SongManager(session)
            expected_data = song_manager.get_artist_by_name(artist_name)
        assert expected_data == json_data

    @mock.patch('fureon.site_controls.MainStreamControls.add_song_with_user_request_to_playlist')
    def test_user_request_blocking(self, mock_song_request):
        with mock.patch.object(config, 'request_ip_whitelist', set()):
            song_id = '1'
            url = '/api/request_song'
            post_data = {'song-id': song_id}
            response = self._post_data_to_url(url, post_data)
            assert response.code == 200
            assert mock_song_request.called

    def test_get_icecast_endpoint(self):
        with mock.patch.object(config, 'paths', testing_utils.MOCK_CONFIG_PATHS):
            url = '/api/stream_endpoint'
            response = self._fetch_response_data_from_url(url)
            assert response.code == 200
            json_data = json.loads(response.body)
            expected_data = {
                'stream_endpoint': testing_utils.MOCK_CONFIG_PATHS['stream_endpoint']
            }
            assert expected_data == json_data

    def _post_data_to_url(self, url, post_data):
        self.http_client.fetch(self.get_url(url), self.stop,
                               method='POST', body=urlencode(post_data)
                               )
        return self.wait()

    def _fetch_response_data_from_url(self, url):
        self.http_client.fetch(self.get_url(url), self.stop)
        return self.wait()
