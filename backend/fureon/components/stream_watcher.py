import threading
import subprocess

from tornado import ioloop

from fureon.components.mixins import SingletonMixin


class StreamPlayerWatcher(threading.Thread, SingletonMixin):
    def __init__(self):
        super(StreamPlayerWatcher, self).__init__()
        from fureon.app import main_stream_controller
        self._stream_controller = main_stream_controller
        self._tornado_ioloop_callback = ioloop.IOLoop.instance().add_callback
        self.running = False
        self.daemon = True

    def run(self):
        while True:
            while self.running:
                proc = subprocess.Popen(['mpc', 'idle'], stdout=subprocess.PIPE)
                line = proc.stdout.readline()
                if str.strip(line) == 'player':
                    self._tornado_ioloop_callback(
                        self._stream_controller.transition_to_next_song
                    )
