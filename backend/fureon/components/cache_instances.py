from fureon import config
from fureon.utils import cache


song_cache = cache.SongCache(**config.cache)
