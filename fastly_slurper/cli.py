"""
fastly_slurper.cli
~~~~~~~~~~~~~~~~~~

:copyright: (c) 2016 Disqus, Inc.
:license: Apache, see LICENSE for more details.
"""
import logging
import click

from . import __version__, slurper

log = logging.getLogger(__name__)


def _make_services(ctx, param, value):
    return tuple(service.split(':', 1) for service in value)


def _make_netaddr(ctx, param, value):
    if ':' not in value:
        return value, 8125

    try:
        host, port = value.rsplit(':', 1)
        return host, int(port)
    except ValueError:
        raise click.BadParameter('host needs to be of form \'IP:PORT\'')


@click.command()
@click.option('--delay', default=1.0, type=float)
@click.option('--statsd', default='localhost', callback=_make_netaddr)
@click.option('--service', 'services', multiple=True, required=True, callback=_make_services)
@click.option('--prefix', default='fastly')
@click.option('--api-key', required=True)
@click.option('--verbose', default=False, is_flag=True)
def slurper(delay, statsd, services, prefix, api_key, verbose):
    logging.basicConfig(
        level=verbose and logging.DEBUG or logging.INFO,
        format='%(asctime)s| %(name)s/%(processName)s[%(process)d]-%(threadName)s[%(thread)d]: '
               '%(message)s @%(funcName)s:%(lineno)d #%(levelname)s',
    )

    log.info('Fastly slurper v%s', __version__)

    client = slurper.Fastly(api_key)
    publisher = slurper.StatsdClient(statsd, prefix)

    workers = [slurper.RecorderWorker(client, publisher, service, delay) for service in services]

    log.info('Spawning slurpers (%d)', len(workers))
    [w.start() for w in workers]

    log.info('Waiting on workers (%d) to complete', len(workers))
    [w.join() for w in workers]


def main():
    return slurper(auto_envvar_prefix='SLURPER')
