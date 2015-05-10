import time

import pytest

from fureon.utils import cache
from tests import testing_utils


class TestCache(object):
    @classmethod
    def setup_class(cls):
        cls._cache = testing_utils.create_mock_cache_from_class(cache.Cache)

    def teardown_method(self, method):
        self._cache.flush_db()

    def test_set_get_and_delete_key_value(self):
        self._cache.set_key_value('1', '2')
        assert '2' == self._cache.get_key_value('1')
        self._cache.delete_key_value('1')
        assert None == self._cache.get_key_value('1')

    def test_flushdb(self):
        test_keys = ['1', '2', '3', '4', '5']
        test_values = ['10', '20', '30', '40', '50']
        map(self._cache.set_key_value, test_keys, test_values)
        assert all(
            value == self._cache.get_key_value(key) \
            for key, value in zip(test_keys, test_values)
        )

        test_values = [None for value in range(len(test_values))]
        self._cache.flush_db()
        assert all(
            value == self._cache.get_key_value(key) \
            for key, value in zip(test_keys, test_values)
        )

    @pytest.mark.slow
    def test_set_key_value_with_expiration_and_check_ttl(self):
        self._cache.set_key_value_with_expiration('1', '2', '10')
        assert '2' == self._cache.get_key_value('1')
        self._cache.delete_key_value('1')
        assert None == self._cache.get_key_value('1')
        self._cache.set_key_value_with_expiration('1', '2', 1)
        assert '2' == self._cache.get_key_value('1')
        assert 1L == self._cache.check_ttl('1')
        time.sleep(1.2)
        assert None == self._cache.get_key_value('1')

class TestSongCache(object):
    @classmethod
    def setup_class(cls):
        cls._cache = testing_utils.create_mock_cache_from_class(cache.SongCache)

    def teardown_method(self, method):
        self._cache.flush_db()

    def test_set_song_request_block_with_ttl(self):
        self._cache.set_song_request_block_with_ttl('1', 3)
        song_key = self._cache._get_song_key_from_id('1')
        assert '' == self._cache.get_key_value(song_key)

    def test_get_song_block_ttl(self):
        self._cache.set_song_request_block_with_ttl('1', 3)
        # song_key = self._cache._get_song_key_from_id('1')
        assert 150L <= self._cache.get_song_block_ttl('1')
    
    def test_get_total_number_of_blocked_songs(self):
        test_song_ids = [1, 2, 3, 4, 5]
        test_ttls = [3, 3, 3, 3, 3]
        map(
            self._cache.set_song_request_block_with_ttl,
            test_song_ids, test_ttls
        )
        assert len(test_song_ids) == self._cache.get_total_number_of_blocked_songs()


