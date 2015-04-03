# Fureon (tentative)
Fureon is a way to build and listen to a music library with friends.  Heavily inspired by [plug.dj](https://plug.dj/), [r-a-dio](https://r-a-d.io/), and [Soundcloud](https://soundcloud.com/), it sets up a server where users contribute to build a global song library and can listen in on a main global music stream.  Users can request songs from the library to be played on the main stream to share with others tuning in.  Alternatively, they can freely stream and listen to any of the songs in the library.

### Installation
Fureon has three main external dependencies:
mpd/mpc
icecast2
redis

Install and set up mpd/mpc to work as a source for icecast2.  Here's a [concise guide](https://www.cupfighter.net/2013/11/building-your-own-radio-station-with-mpd-mpc-and-icecast2-on-debian) on how to set up mpd/mpc to stream with icecast2.

redis should typically be available in the repos for most linux distros.

After that, the backend can be quickly installed using setuptools with the provided setup.py.  In /backend create and source a virtualenv then execute setup.py with install or develop:

```sh
$ python ./setup.py install
```

All python dependencies should be covered by the install.  Several parameters in /backend/fureon/config.py need to be set before the app can run.
##### Paths
Fureon needs to know where to look for songs and where to save album art.
```python
paths = {
    'song_directory' : '/home/user/music/',
    'static_folder_path' : '/var/www/fureon.site.com/frontend/static/',
    'log_file' : os.path.join(PARENT_DIRECTORY, 'fureon.log'
}
```
song_directory needs to be set to the same directory as mpd's song directory.
static_folder_path needs should be set to where static files intend to be served.  This is used as the target location to save album art.  Leaving it blank will have the app not save any album art.

##### Database
Fureon uses SQLAlchemy which requires a database connection.  The connection parameters must be set for the database used.  An example for PostgreSQL:
```python
database = {
    'drivername' : 'postgres',
    'host' : 'localhost',
    'port' : '5432',
    'username' : 'myusername',
    'password' : 'supersecretpassword',
    'database' : 'fureon',
}
```
Or for a simple SQLite db:
```python
database = {
    'drivername' : 'sqlite',
    'host' : '',
    'port' : '',
    'username' : '',
    'password' : '',
    'database' : 'fureon.db',
}
```
##### Cache
Fureon uses redis to keep track of the delay for song and user request blocking.
```python
cache = {
    'host' : 'localhost',
    'port' : '6379',
}
```
These are the default redis connection parameters.  Change them if the system's redis server is set differently.

Once all the configuration is done, run the app with:
```sh
$ fureon-start
```

Implementation
---
### Backend

The Fureon backend runs on [tornado](http://www.tornadoweb.org/en/stable/) + [SQLAlchemy](http://www.sqlalchemy.org/) + [redis](http://redis.io/).  Tornado was chosen for its performance, modularity and light weight, as well as its ease in implementing websockets.  The database is abstracted into models with SQLAlchemy and redis is used as both a cache as well as a means to have a data structure that can expire with time.  Fureon shares the music db directory of the system's mpd installation and can scan the directory while also extracting the metadata with [mutagen](https://pypi.python.org/pypi/mutagen) into the database models.

Fureon currently handles playing music to the main stream with [mpd](http://www.musicpd.org/) controlled by [mpc](http://www.musicpd.org/clients/mpc/).  The mpd output is used as an [icecast](http://icecast.org/) source to serve listeners.  The app watches any changes to mpd with the mpc idle cli command, and upon events such as a transition to the next song, it adds a callback to the tornado ioloop which signals changes to the fureon db playlist which then sends commands back to mpc to update the mpd playlist keeping both the mpd and fureon db playlists consistent.

Many functions in the Fureon backend can be accessed from it's RESTlike API.  This includes searching for songs, getting the current playlist, getting song data, as well as requesting songs.

##### 

### Frontend

Frontend work will be done in cooperation with github user [Rifu](https://github.com/Rifu) working on the [anzu](https://github.com/Rifu/anzu) repo.  Powered by Ember.js, it will request the necessary data from the backend's RESTlike endpoints to build the app UI.  The projects will merge eventually once a final name is settled and a good merging point is reached.

Backend API
---
The Fureon backend API has the following endpoints:
```sh
$ /api
```
Returns this description of all api endpoints in JSON format.

```sh
$ /api/playlist
```
Returns the current playlist with the order given as keys.  Includes: song title, song artist, song id, song duration, and whether the song was user requested or not.

```sh
$ /api/song/find?song-id=<song_id>
```
Returns the full details of a single song with the id \<song_id\>.  Data includes (if available): id, title, artist, album, trackno, date, genre, duration, file_path, art_path, datetime_added, tags, play_count, fave_count.

```sh
$ /api/album/find?name=<album_name>
```
An exact search for albums with the name \<album_name\>.  Will return a numbered object with song titles, song artists, song_ids, tracknos, dates, fave_count, play_count, and art_paths.

```sh
$ /api/artist?name=<artist_name>
```
An exact search for albums with the name \<artist_name\>.  Will return a numbered object with song titles, song_ids, album names, dates, play_count, fave_count.

```sh
$ /api/request_song
```
POST method with params: song-id=\<song_id\>.  Sends a song request to update the main stream playlist with the requested song.  User requested songs have higher priority than random songs.  Stream playlist order is requested songs in added order, then random songs in added order.

Features to Add / To Do (Priority Highest to Lowest)
---
##### User Request Blocking
Users should only be able to request a certain amount of times within a timespan. This is to prevent a single user from hijacking the stream with requests.  Implement with redis in the same way the song request blocking works but with the requester's IP instead of song_id.

##### User Logins
This is for the user to login in order to mark songs as favorites and accessing a favorites page.  Will require adding a user model as well as an authentication system.  Tornado has authentication built in and storing passwords will most likely be done with passlib.

##### API Request Validation
Validate the arguments to an API request and return useful error responses if the request is incorrect.

##### Streaming Individual Songs
Besides the main stream, users should be able to listen to any track that's on the database separately.

##### Websocket Feed When Playlist Updates
Whenever another user sends a request or a song ends, the playlist order changes.  Use websockets to keep a constant connection and send the user playlist change events.  Implementation will most likely be done with [sockjs-tornad](https://pypi.python.org/pypi/sockjs-tornado)

##### IRC Bot Control
A way to control the stream by sending commands to an IRC bot.  Looking to add a plugin for [kochira](https://github.com/rfw/kochira)

