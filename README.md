# Fureon
Fureon is a way to build and listen to a music library with friends.  Heavily inspired by [plug.dj](https://plug.dj/), [r-a-dio](https://r-a-d.io/), and [Soundcloud](https://soundcloud.com/), it sets up a server where users contribute to build a global song library and can listen in on a main global music stream.  Users can request songs from the library to be played on the main stream to share with others tuning in.  Alternatively, they can freely stream and listen to any of the songs in the library.

##### Installation (incomplete)
Fureon has three main external dependencies:
mpd/mpc
icecast2
exiftool

Install and set up mpd/mpc to work as a source for icecast2.  Here's a [concise guide](https://www.cupfighter.net/2013/11/building-your-own-radio-station-with-mpd-mpc-and-icecast2-on-debian) on how to set up mpd/mpc to stream with icecast2.

As for exiftool, it simply needs to be extracted to an exectuable location.  I recommend ./backend/ext_apps/exiftool/

Implementation
---
### Backend (incomplete)

##### Main Music Stream
Fureon currently handles playing music to the main stream with [mpd](http://www.musicpd.org/) controlled by [mpc](http://www.musicpd.org/clients/mpc/).  The mpd output is used as an [icecast](http://icecast.org/) source to serve listeners
