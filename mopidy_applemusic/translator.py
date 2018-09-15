from __future__ import unicode_literals

import hashlib

from mopidy.models import Ref

def albumToRef(album):
    """Convert a mopidy album to a mopidy ref."""
    name = ''
    if album.name:
        name += album.name
    else:
        name += 'Unknown Album'
    if (len(album.artists)) > 0:
        name += ' - '

    firstArtist = True
    for artist in album.artists:
        if not firstArtist:
            name += ', '
        name += artist.name
        firstArtist = False
    
    return Ref.directory(uri=album.uri, name=name)

def trackToRef(track):
    """Convert a mopidy track to a mopidy ref."""
    name = track.name
    if (len(track.artists)) > 0:
        name += ' - '
    for artist in track.artists:
        if len(name) > 0:
            name += ', '
        name += artist.name

    return Ref.track(uri=track.uri, name=name)
