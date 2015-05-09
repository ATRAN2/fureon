import tornado
from tornado.options import define, options, parse_command_line

from fureon import db_operations, site_controls, config
from fureon.web import api_handlers
from fureon.components.cache_instances import song_cache

define('port', default=8888, help='determines what port to run the application on', type=int)
define('debug', default=False, help='set to True to run in debug mode')

main_stream_controller = site_controls.MainStreamControls(song_cache)

api_endpoints = [
    (r'/api', api_handlers.APIRootHandler),
    (r'/api/playlist', api_handlers.PlaylistSongsHandler),
    (r'/api/song/find', api_handlers.FindSongByIDHandler),
    (r'/api/request_song', api_handlers.RequestSongByIDHandler),
    (r'/api/album/find', api_handlers.FindAlbumByNameHandler),
    (r'/api/artist/find', api_handlers.FindArtistByNameHandler),
    (r'/api/stream_endpoint', api_handlers.GetStreamEndpointHandler),
]

def main():
    parse_command_line()
    app = tornado.web.Application(
        api_endpoints,
        debug=options.debug,
    )
    app.listen(options.port)

    db_operations.connect_to_db()

    main_stream_controller.initialize_stream()
    main_stream_controller.run_stream()

    tornado.ioloop.IOLoop.instance().start()

if __name__ == '__main__':
    main()

