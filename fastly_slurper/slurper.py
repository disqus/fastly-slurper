"""
fastly_slurper.slurper
~~~~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2016 Disqus, Inc.
:license: Apache, see LICENSE for more details.
"""
from __future__ import (absolute_import, division, generators, nested_scopes,
                        print_function, unicode_literals, with_statement)

import logging
import threading
import requests
import six

from datetime import datetime
from os.path import join
from time import sleep, time
from pystatsd import Client as StatsdClient

from . import __version__

log = logging.getLogger(__name__)

_FASTLY_API_BASE_URI = 'https://rt.fastly.com/'
_USER_AGENT = 'fastly-slurpy/%s' % __version__


class Fastly(requests.Session):
    base = _FASTLY_API_BASE_URI
    user_agent = _USER_AGENT

    def __init__(self, api_key, *args, **kwargs):
        self.api_key = api_key

        super(Fastly, self).__init__(*args, **kwargs)

        self.headers.update({
            'Fastly-Key': self.api_key,
            'User-Agent': self.user_agent,
        })

    def _ensure_abs_url(self, url):
        # ensure abs
        if '://' not in url:
            url = '%s%s' % (self.base, url)
        return url

    def request(self, method, url, *args, **kwargs):
        url = self._ensure_abs_url(url)
        return super(Fastly, self).request(method=method, url=url, **kwargs)


class RecorderWorker(threading.Thread):

    def __init__(self, client, publisher, service, delay=1.0):
        super(RecorderWorker, self).__init__()
        self.daemon = True

        self.client = client
        self.publisher = publisher
        self.name, self.channel = service
        self.delay = delay

    def timing(self, stat, time):
        stat = '%s.%s' % (self.name, stat)
        return self.publisher.timing(stat, time)

    def gauge(self, stat, time):
        stat = '%s.%s' % (self.name, stat)
        return self.publisher.gauge(stat, time)

    def url_for_timestamp(self, ts):
        # Convert timestamp to str and remove the decimal
        strts = ('%.9f' % ts).translate(None, '.')
        return join('channel', self.channel, 'ts', strts)

    def get_stats(self, ts):
        response = self.client.get(self.url_for_timestamp(ts)).json()
        return response['Data']

    def record_stats(self, message):
        for stats in message:
            if 'datacenter' in stats:
                for dc, dcstats in six.iteritems(stats['datacenter']):
                    for stat, val in six.iteritems(dcstats):
                        if stat == 'miss_histogram':
                            continue

                        if stat.endswith('_time'):
                            t = stat.split('_')[0]
                            if dcstats[t]:
                                val = val / dcstats[t] * 1000

                        stat_name = '%s.%s' % (dc, stat)
                        self.timing(stat_name, val)

                self.gauge('last_record', int(time()))

    def run(self):
        self.running = True

        while self.running:
            ts = time()

            try:
                log.debug('Fetching stats for ts=%s'.ts)
                stats = self.get_stats(ts)

                log.info('Recording stats for ts=%s: %r', ts, stats)
                self.record_stats(stats)
            except Exception:
                log.exception('Failed slurp for ts=%s; exception follows:', ts)

            if time() <= ts + self.delay:
                sleep(self.delay)
