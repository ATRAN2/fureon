from fureon.components.cache_instances import song_cache

def invalidate_cached_playlist(func):
    def func_wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    song_cache.flush_playlist()
    return func_wrapper
