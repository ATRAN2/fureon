import subprocess


NULL_DEVICE = '/dev/null'
class StreamPlayer(object):
    @staticmethod
    def send_command(command, response=None):
        proc = subprocess.Popen(['mpc', command], stdout=NULL_DEVICE)
        return response

    @staticmethod
    def currently_playing():
        proc = subprocess.Popen(['mpc'], stdout=NULL_DEVICE)
        line = proc.stdout.readline():
            if line.startswith('volume: n/a'):
                return 'No song is currently playing'
            else:
                return line.decode('utf-8')

    @staticmethod
    def play():
        return send_command('play', 'Played player')

    @staticmethod
    def stop():
        return send_command('stop', 'Stopped player')

    @staticmethod
    def clear():
        return send_command('clear', 'Cleared player playlist')

    @staticmethod
    def crop():
        return send_command('crop', 'Cleared player playlist except currently playing song')

    @staticmethod
    def add(song_path):
        response_message = 'Added {0} to the playlist'.format(song_path)
        return send_command('add', response_message)

    @staticmethod
    def remove(song_position=1)
        response_message = 'Removed the song in position {0} of the playlist'.format(str(song_position))
        return send_command('del', response_message)

