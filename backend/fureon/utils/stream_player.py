import subprocess

from fureon import config


class StreamPlayer(object):
    DEFAULT_NULL_DEVICE = '/dev/null'
    
    def __init__(self, null_device=DEFAULT_NULL_DEVICE):
        self.null_device = null_device

    def send_command(self, command, response=None):
        full_command = ['mpc'] + command
        proc = subprocess.Popen(full_command, stdout=self.null_device).wait()
        return response

    def currently_playing(self):
        proc = subprocess.Popen(['mpc'], stdout=subprocess.PIPE)
        line = proc.stdout.readline()
        if line.startswith('volume: n/a'):
            return 'No song is currently playing'
        else:
            return line.decode('utf-8')

    def play(self):
        return self.send_command(['play'], respone='Played player')

    def stop(self):
        return self.send_command(['stop'], response='Stopped player')

    def clear(self):
        return self.send_command(['clear'], response='Cleared player playlist')

    def crop(self):
        return self.send_command(['crop'], response='Cleared player playlist except currently playing song')

    def add(self, song_path):
        response_message = 'Added {0} to the playlist'.format(song_path)
        relative_song_path = self._get_relative_mpd_song_path(song_path)
        return self.send_command(['add', relative_song_path], response=response_message)

    def remove(self, song_position=1):
        response_message = 'Removed the song in position {0} of the playlist'.format(str(song_position))
        return self.send_command(['del', song_position], response=response_message)

    def _get_relative_mpd_song_path(self, absolute_song_path):
        return os.path.relpath(absolute_song_path, config.paths['song_directory'])

