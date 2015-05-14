ENDPOINT_DESCRIPTIONS = {
    u'/api': u'Returns this description of all api endpoints in JSON format.',
    u'/api/playlist':
        (u'Returns the current playlist with the order given as keys. '
         'Includes: song title, song artist, song id, song duration, '
         'and whether, the song was user requested or not.'),
    u'/api/song/find?song-id=<song_id>':
        (u'Returns the full details of a single song with the id '
         '<song_id>.  Data includes (if available): id, title, artist, '
         'album, trackno, date, genre, duration, file_path, art_path, '
         'datetime_added, tags, play_count, fave_count.'),
    u'/api/album/find?name=<album_name>':
        (u'An exact search for albums with the name <album_name>. Will '
         'return a numbered object with song titles, song artists, '
         'song_ids, tracknos, dates, fave_count, play_count, and art_paths.'),
    u'/api/artist/find?name=<artist_name>':
        (u'An exact search for the artist with the name <artist_name>. '
         'Will return a numbered object with song titles, song_ids, '
         'album names, dates, play_count, fave_count, '),
    u'/api/request_song':
        (u'POST method with params: song-id=<song_id>. Sends a song '
         'request to update the main stream playlist with the requested '
         'song.  User requested songs have higher priority than random '
         'songs.  Stream playlist order is requested songs in added '
         'order, then random songs in added order.'),
}
