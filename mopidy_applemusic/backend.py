import pykka

from mopidy import backend, models
from mopidy_applemusic import logger
from mopidy_applemusic.translator import albumToRef

from applepymusic import AppleMusicClient

ROOT = 'applemusic:root'
MY_ALBUMS = 'applemusic:myalbums'

ARTIST_PREFIX = 'applemusic:artist:'
ALBUM_PREFIX = 'applemusic:album:'

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

    def browse(self, uri):
        logger.info("Browse %s", uri)
        if uri == ROOT:
            return self.sub_directory
        elif uri == MY_ALBUMS:
            return self.browseAlbums()
        logger.info(self.appleMusicClient.user_songs(limit=10))
        pass

    def lookup(self, uri):
        logger.info("Looking up %s", uri)
        pass

    # Helper Methods #

    def browseAlbums(self):
        albums = self.appleMusicClient.user_albums(limit=10, include=['artists'])

        logger.info(albums)

        albumData = albums['data']

        if not albumData:
            logger.error("Could not load my albums")
            return []

        return list(map(lambda album: albumToRef(album), self.albumDataToRefs(albumData)))

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

class AppleMusicPlaybackProvider(backend.PlaybackProvider):
    def __init__(self, audio, backend, appleMusicClient):
        super(AppleMusicPlaybackProvider, self).__init__(audio, backend)
        self.appleMusicClient = appleMusicClient

    def translate_uri(self, uri):
        logger.info("Attempting to translate uri %s", uri)
        # track = resolve_track(uri, True)
        return uri
        if track is not None:
            return track.uri
        else:
            return None
