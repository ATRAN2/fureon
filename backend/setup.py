#!/usr/bin/env python2.7

from setuptools import setup, find_packages

setup(name = 'fureon',
    version = '0.0',
    description = 'Crowd enabled music streamer and library',
    author='Andy Tran',
    author_email = 'andy@atran.net',
    url = '',
    packages = find_packages(),
    include_package_data = True,
    zip_safe = False,
    install_requires = [
        'tornado',
        'sqlalchemy',
        'mutagen',
        'pytest',
        'pytest-cov',
        'redis',
    ],
    entry_points = {
        'console_scripts': [
            'fureon-start = fureon.app:main',
        ]
    }
)


