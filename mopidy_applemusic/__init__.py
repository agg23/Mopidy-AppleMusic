from __future__ import absolute_import, unicode_literals

import logging
import os

from mopidy import config, exceptions, ext

__version__ = '0.1'

# If you need to log, use loggers named after the current Python module
logger = logging.getLogger(__name__)

class Extension(ext.Extension):

    dist_name = 'Mopidy-AppleMusic'
    ext_name = 'applemusic'
    version = __version__

    def get_default_config(self):
        conf_file = os.path.join(os.path.dirname(__file__), 'ext.conf')
        return config.read(conf_file)

    def get_config_schema(self):
        schema = super(Extension, self).get_config_schema()
        schema['developertoken'] = config.Secret()
        schema['usertoken'] = config.Secret()
        return schema

    def get_command(self):
        # from .commands import SoundspotCommand
        # return SoundspotCommand()
        pass

    def validate_environment(self):
        # Any manual checks of the environment to fail early.
        # Dependencies described by setup.py are checked by Mopidy, so you
        # should not check their presence here.
        pass

    def setup(self, registry):
        # You will typically only do one of the following things in a
        # single extension.

        # Register a frontend
        # from .frontend import SoundspotFrontend
        # registry.add('frontend', SoundspotFrontend)

        # Register a backend
        from .backend import AppleMusicBackend
        registry.add('backend', AppleMusicBackend)

        # Or nothing to register e.g. command extension
        pass