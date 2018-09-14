from __future__ import absolute_import, unicode_literals

import re
from setuptools import setup, find_packages


def get_version(filename):
    content = open(filename).read()
    metadata = dict(re.findall("__([a-z]+)__ = '([^']+)'", content))
    return metadata['version']


setup(
    name='Mopidy-AppleMusic',
    version=get_version('mopidy_applemusic/__init__.py'),
    url='https://github.com/agg23/Mopidy-AppleMusic',
    license='MIT License',
    author='Adam Gastineau',
    author_email='adam@appcannonsoftware.com',
    description='Apple Music backend for Mopidy',
    long_description=open('README.rst').read(),
    packages=find_packages(exclude=['tests', 'tests.*']),
    zip_safe=False,
    include_package_data=True,
    install_requires=[
        'setuptools',
        'Mopidy >= 0.14',
        'Pykka >= 1.1',
        'apple-py-music',
    ],
    entry_points={
        'mopidy.ext': [
            'applemusic = mopidy_applemusic:Extension',
        ],
    },
    classifiers=[
        'Environment :: No Input/Output (Daemon)',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Topic :: Multimedia :: Sound/Audio :: Players',
    ],
)