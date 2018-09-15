import pykka

from mopidy import backend, models
from mopidy_applemusic import logger
from mopidy_applemusic.translator import albumToRef, trackToRef

from applepymusic import AppleMusicClient

ROOT = 'applemusic:root'
MY_ALBUMS = 'applemusic:myalbums'

ARTIST_PREFIX = 'applemusic:artist:'
ALBUM_PREFIX = 'applemusic:album:'
TRACK_PREFIX = 'applemusic:track:'

class AppleMusicBackend(pykka.ThreadingActor, backend.Backend):
    def __init__(self, config, audio):
        super(AppleMusicBackend, self).__init__()
        self.audio = audio
        self.config = config

        developerToken = config['applemusic']['developertoken']
        userToken = config['applemusic']['usertoken']

        logger.info(config)

        self.appleMusicClient = AppleMusicClient(developerToken, userToken)

        self.library = AppleMusicLibraryProvider(backend=self, appleMusicClient=self.appleMusicClient)
        self.playback = AppleMusicPlaybackProvider(audio=audio, backend=self, appleMusicClient=self.appleMusicClient)

        self.uri_schemes = ['applemusic']

class AppleMusicLibraryProvider(backend.LibraryProvider):
    def __init__(self, backend, appleMusicClient):
        super(AppleMusicLibraryProvider, self).__init__(backend)
        self.appleMusicClient = appleMusicClient

        self.root_directory = models.Ref.directory(uri=ROOT, name='Apple Music')

        self.sub_directory = [
            models.Ref.directory(uri=MY_ALBUMS, name='Albums')
        ]

        self.trackCache = {}

    def browse(self, uri):
        logger.info("Browse %s", uri)
        parts = uri.split(':')
        prefix = ''

        if len(parts) > 1:
            prefix = ':'.join(parts[0:2]) + ':'

        logger.info("Prefix %s", prefix)

        if uri == ROOT:
            logger.info("Browsing root")
            return self.sub_directory

        # All albums
        elif uri == MY_ALBUMS:
            logger.info("Browsing my albums")
            return self.browseAlbums()

        # Single album
        elif prefix == ALBUM_PREFIX:
            logger.info("Browsing album")
            return self.browseAlbum(parts[2])

        logger.info(self.appleMusicClient.user_songs(limit=10))
        pass

    def lookup(self, uri):
        logger.info("Looking up %s", uri)

        parts = uri.split(':')
        prefix = ''

        if len(parts) > 1:
            prefix = ':'.join(parts[0:2]) + ':'

        if prefix == TRACK_PREFIX:
            return self.lookupTrack(parts[2], uri)
        pass

    # Helper Methods #

    def browseAlbums(self):
        albums = self.appleMusicClient.user_albums(limit=10, include=['artists'])

        albumData = albums['data']

        if not albumData:
            logger.error("Could not load my albums")
            return []

        return list(map(lambda album: albumToRef(album), self.albumDataToRefs(albumData)))

    def browseAlbum(self, albumId):
        album = self.appleMusicClient.user_get_album(albumId, include=['artists'])

        albumData = album['data']

        if not albumData:
            logger.error("Could not load album")
            return []

        albumRef = self.albumDataToRefs(albumData)[0]

        logger.info(albumRef)

        tracks = self.trackRelationshipsToRefs(albumData[0]['relationships'], albumRef)
        trackRefs = []

        for track in tracks:
            if not track:
                continue
            
            self.trackCache[track.uri] = track
            trackRefs.append(trackToRef(track))

        return trackRefs

    def lookupTrack(self, trackId, uri):
        if self.trackCache[uri]:
            return [self.trackCache[uri]]
        
        trackJSON = self.appleMusicClient.user_get_song(trackId)
        trackData = trackJSON['data']

        if len(trackData) != 1:
            logger.error("Could not load track %s", trackId)
            return []

        name = trackJSON['attributes']['name']
        length = trackJSON['attributes']['durationInMillis']

        track = models.Track(uri=uri, name=name, album=albumRef, length=length)

        self.trackCache[uri] = track
        
        return [track]

    # Reference Builders #

    def albumDataToRefs(self, albumData):
        albums = []

        for albumJSON in albumData:
            attributes = albumJSON['attributes']

            uri = ALBUM_PREFIX+albumJSON['id']
            name = attributes['name']
            artists = self.artistRelationshipsToRefs(albumJSON['relationships'])
            num_tracks = attributes['trackCount']

            album = models.Album(uri=uri, name=name, artists=artists, num_tracks=num_tracks)
            albums.append(album)

        return albums

    def artistRelationshipsToRefs(self, relationships):
        artists = []

        if not relationships['artists']:
            return []

        for artistJSON in relationships['artists']['data']:
            uri = ARTIST_PREFIX + artistJSON['id']
            name = artistJSON['attributes']['name']

            artist = models.Artist(uri=uri, name=name)
            artists.append(artist)

        return artists

    def trackRelationshipsToRefs(self, relationships, albumRef):
        tracks = []

        if not relationships['tracks']:
            return []

        for trackJSON in relationships['tracks']['data']:
            uri = TRACK_PREFIX + trackJSON['id']
            name = trackJSON['attributes']['name']
            artists = albumRef.artists
            length = trackJSON['attributes']['durationInMillis']

            # track = models.Track(uri=uri, name=name, artists=artists, album=albumRef, length=length)
            track = models.Track(uri=uri, name=name, album=albumRef, length=length)
            tracks.append(track)

        return tracks

class AppleMusicPlaybackProvider(backend.PlaybackProvider):
    def __init__(self, audio, backend, appleMusicClient):
        super(AppleMusicPlaybackProvider, self).__init__(audio, backend)
        self.appleMusicClient = appleMusicClient

    def translate_uri(self, uri):
        logger.info("Attempting to translate uri %s", uri)

        parts = uri.split(':')

        if len(parts) < 1:
            return None

        track = self.lookupTrack(parts[len(parts)-1])

        logger.info("Selected track url %s", track)

        if track is not None:
            return track
        else:
            return None

        
    def lookupTrack(self, trackId):
        track = self.appleMusicClient.get_play_song(trackId)
        songList = track['songList']

        if len(songList) != 1:
            logger.error("Could not load track %s", trackId)
            return None
        
        trackData = songList[0]
        
        assets = trackData['assets'][0]
        metadata = assets['metadata']

        url = assets['URL']

        return url
