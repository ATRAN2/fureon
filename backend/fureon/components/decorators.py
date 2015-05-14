class invalidate_cached_playlist(object):
    def __init__(self, cache_name):
        self._cache_name = cache_name

    def __call__(self, func):
        def wrapped_func(*args, **kwargs):
            return_values = func(*args, **kwargs)
            if hasattr(args[0], self._cache_name):
                cache = getattr(args[0], self._cache_name)
                cache.flush_playlist()
            return return_values
        return wrapped_func
