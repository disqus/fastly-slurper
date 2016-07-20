"""
fastly_slurper.slurper
~~~~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2015 Disqus, Inc.
:license: Apache, see LICENSE for more details.
"""
import sys
import threading
from time import time, sleep
from datetime import datetime
from os.path import join

import requests
from pystatsd import Client as StatsdClient


class Statsd(StatsdClient):
    def __init__(self, address=('localhost', 8125), prefix=None, verbose=True):
        self.verbose = verbose
        super(Statsd, self).__init__(address[0], address[1], prefix)

    def timing(self, stat, time):
        self._log('timing', stat, time)
        super(Statsd, self).timing(stat, time)

    def gauge(self, stat, time):
        self._log('gauge', stat, time)
        super(Statsd, self).gauge(stat, time)

    def _log(self, type, stat, value):
        if self.verbose:
            sys.stderr.write(
                '{now} [{type}] {stat} {value}\n'.format(
                    now=datetime.now(), type=type,
                    stat=stat if self.prefix is None else '.'.join((self.prefix, stat)),
                    value=value,
                )
            )


class Fastly(requests.Session):
    base = 'https://rt.fastly.com/'
    user_agent = 'fastly-slurper/1.0'

    def __init__(self, api_key):
        super(Fastly, self).__init__()

        self.headers.update({
            'Fastly-Key': api_key,
            'User-Agent': self.user_agent,
        })

    def request(self, method, url, **kwargs):
        return super(Fastly, self).request(method=method, url=self.base+url, **kwargs)


class RecorderWorker(threading.Thread):
    def __init__(self, client, publisher, service, delay=1.0):
        super(RecorderWorker, self).__init__()
        self.daemon = True

        self.client = client
        self.publisher = publisher
        self.name, self.channel = service
        self.delay = delay

    def timing(self, stat, time):
        self.publisher.timing(self.name + '.' + stat, time)

    def gauge(self, stat, time):
        self.publisher.gauge(self.name + '.' + stat, time)

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
                for dc, dcstats in stats['datacenter'].iteritems():
                    for stat, val in dcstats.iteritems():
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
        while True:
            try:
                self.record_stats(self.get_stats(time()))
            except Exception:
                import traceback
                traceback.print_exc(file=sys.stderr)
            sleep(self.delay)
