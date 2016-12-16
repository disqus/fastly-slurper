#!/usr/bin/env python
"""
fastly-slurper
~~~~~~~~~~~~~~

:copyright: (c) 2016 Disqus, Inc.
:license: Apache, see LICENSE for more details.
"""
import glob
import os

from pip.download import PipSession
from pip.req import parse_requirements
from setuptools import find_packages, setup


def setup_requirements(pattern='requirements/*.txt', install_combined=False):
    """
    Parse a glob of requirements and return a dictionary of setup() options.
    Create a dictionary that holds your options to setup() and update it using this.
    Pass that as kwargs into setup(), viola

    Any files that are not a standard option name (ie install, tests, setup) are added to extras_require with their
    basename minus ext. An extra key is added to extras_require: 'all', that contains all distinct reqs combined.

    If you're running this for a Docker build, set install_combined=True.
    This will set install_requires to all distinct reqs combined.

    :param str pattern: Glob pattern to find requirements files
    :param bool install_combined: Set True to set install_requires to extras_require['all']
    :return dict: Dictionary of parsed setup() options
    """
    key_map = {
        'install.txt': 'install_requires',
        'tests.txt': 'tests_require',
        'setup.txt': 'setup_requires',
    }
    ret = {v: [] for v in key_map.values()}
    extras = ret['extras_require'] = {}
    all_ = set()
    session = PipSession()

    for full_fn in glob.glob(pattern):
        # Parse file
        reqs = [str(r.req) for r in parse_requirements(full_fn, session=session)]
        all_.update(reqs)

        fn = os.path.basename(full_fn)
        key = key_map.get(fn)
        if key:
            ret[key].extend(reqs)
        else:
            # Remove extension
            key, _ = os.path.splitext(fn)
            extras[key] = reqs

    if 'all' not in extras:
        extras['all'] = list(all_)

    if install_combined:
        extras['install'] = ret['install_requires']
        ret['install_requires'] = list(all_)

    return ret


def long_description():
    with open('README.rst') as fp:
        return fp.read()


_conf = dict(
    name='fastly-slurper',
    version='0.0.1',
    description='Slurp realtime metrics from Fastly',
    long_description=long_description(),
    author='Disqus',
    author_email='opensource@disqus.com',
    url='https://github.com/disqus/fastly-slurper',
    license='Apache License 2.0',
    packages=find_packages(),
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

_conf.update(setup_requirements())

setup(**_conf)
