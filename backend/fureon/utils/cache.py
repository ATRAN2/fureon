import redis


class Cache(object):
    def __init__(self, host, port, db):
        self._cache = redis.StrictRedis(host=host, port=port, db=db)

    def set_key_value(self, key, value):
        return self._cache.set(key, value)

    def set_key_value_with_expiration(self, key, value, expiration_in_seconds):
        return self._cache.setex(key, expiration_in_seconds, value)

    def get_key_value(self, key):
        return self._cache.get(key)

    def delete_key_value(self, key):
        return self._cache.delete(key)

    def check_ttl(self, key):
        return self._cache.ttl(key)

    def flush_db(self):
        return self._cache.flushdb()

class SongCache(Cache):
    def __init__(self, host, port, db=0):
        super(SongCache, self).__init__(host, port, db)

    def set_song_request_block_with_ttl(self, song_id, ttl_in_minutes):
        song_key = self._get_song_key_from_id(song_id)
        ttl = ttl_in_minutes * 60
        return self.set_key_value_with_expiration(song_key, '', ttl)

    def get_song_block_ttl(self, song_id):
        return self.get_key_value(self._get_song_key_from_id(song_id))

    def get_total_number_of_blocked_songs(self):
        return len(self._cache.keys('song_expiration_ttl_id*'))

    def set_playlist(self, playlist_json_dump):
        return self.set_key_value('stream_playlist_query', playlist_json_dump)

    def get_playlist(self):
        return self.get_key_value('stream_playlist_query')

    def flush_playlist(self):
        return self.delete_key_value('stream_playlist_query')

    def _get_song_key_from_id(self, song_id):
        return 'song_expiration_ttl_id:{0}'.format(song_id)

class UserCache(Cache):
    def __init__(self, host, port, db=1):
        super(UserCache, self).__init__(host, port, db)

    def set_user_request_block_with_ttl(self, user_ip, ttl_in_minutes):
        pass
