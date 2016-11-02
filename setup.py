#!/usr/bin/env python

'''Pi-IO Python client
Basic client for the Pi-IO dbus IO server for the raspberry pi
'''

from distutils.core import setup
from distutils.extension import Extension
from glob import glob
import os

# patch distutils if it's too old to cope with the "classifiers" or
# "download_url" keywords
from sys import version
if version < '2.2.3':
    from distutils.dist import DistributionMetadata
    DistributionMetadata.classifiers = None
    DistributionMetadata.download_url = None

if __name__ == '__main__':
    setup(
        name = 'piio',
        version = "0.3.0",
        description = 'Pi-IO python client',
        long_description = __doc__,
        author = 'Miqra Engineering',
        author_email = 'packaging@miqra.nl',
        maintainer = 'Miqra Engineering Packaging',
        maintainer_email = 'packaging@miqra.nl',
        platforms=['posix'],
        url='',
        license='GPL',
        classifiers = [
            'Development Status :: 5 - Production/Stable',
            'Intended Audience :: End Users/Desktop',
            'License :: OSI Approved :: Gnu Public License',
            'Operating System :: POSIX :: Linux',
            'Programming Language :: Python :: 2',
            ],
        packages=['piio'],
        data_files = [ ],
    )
