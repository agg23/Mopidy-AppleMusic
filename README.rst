****************
Mopidy-AppleMusic
****************

`Mopidy <http://www.mopidy.com/>`_ extension for playing music from
Apple Music/iCloud Music Library.

*Note:* Unfortunately Apple Music audio files are protected by Widevine or Fairplay
encryption (depending on the requesting OS). As such they cannot be played through
this extension. However, user uploaded tracks (through iTunes Match or Apple Music)
are not encrypted and can be played without issue.

Installation
============

Install by running::

    sudo pip install Mopidy-AppleMusic

Configuration
=============

Before starting Mopidy, you must add your Apple Music developer token and user token
to the Mopidy configuration file::

    [applemusic]
    developertoken = 123
    usertoken = 456