import tornado.ioloop
from tornado.options import define, options, parse_command_line

from fureon.web import api_handlers


define('port', default=8888, help='determines what port to run the application on', type=int)
define('debug', default=False, help='set to True to run in debug mode')

def main():
    parse_command_line()

    app = tornado.web.Application(
        [
           (r'/api', api_handlers.APIRootHandler),
        ],
        debug=options.debug,
    )

    app.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == '__main__':
    main()

