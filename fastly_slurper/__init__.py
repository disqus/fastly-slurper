"""
fastly_slurper
~~~~~~~~~~~~~~

:copyright: (c) 2016 Disqus, Inc.
:license: Apache, see LICENSE for more details.
"""
try:
    __version__ = __import__('pkg_resources') \
        .get_distribution('fastly-slurper').version
except Exception:  # pragma: no cover
    __version__ = 'unknown'
