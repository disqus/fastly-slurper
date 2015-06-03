#!/usr/bin/env python
"""
fastly-slurper
~~~~~~~~~~~~~~

:copyright: (c) 2015 Disqus, Inc.
:license: Apache, see LICENSE for more details.
"""
from setuptools import setup, find_packages

install_requires = [
    'click>=4.0,<5.0',
    'pystatsd',
    'requests[security]>=2.7.0,<2.8.0',
]


def long_description():
    with open('README.rst') as fp:
        return fp.read()


setup(
    name='fastly-slurper',
    version='0.0.0.dev',
    description='Slurp realtime metrics from Fastly',
    long_description=long_description(),
    author='Matt Robenolt',
    author_email='matt@disqus.com',
    url='https://github.com/disqus/fastly-slurper',
    license='Apache License 2.0',
    packages=find_packages(),
    install_requires=install_requires,
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'fastly-slurper = fastly_slurper.cli:main',
        ],
    },
    classifiers=[
        'nope',
    ],
)
