import tornado
from tornado.options import define, options, parse_command_line

from fureon import site_controls, config
from fureon.web import api_handlers
from fureon.components.stream_controller_instance import main_stream_controller


define('port', default=8888, help='determines what port to run the application on', type=int)
define('debug', default=False, help='set to True to run in debug mode')

api_endpoints = [
    (r'/api', api_handlers.APIRootHandler),
    (r'/api/playlist', api_handlers.PlaylistSongsHandler),
]

def main():
    parse_command_line()
    app = tornado.web.Application(
        api_endpoints,
        debug=options.debug,
    )
    app.listen(options.port)

    main_stream_controller.initialize_stream()
    main_stream_controller.run_stream()

    tornado.ioloop.IOLoop.instance().start()

if __name__ == '__main__':
    main()

