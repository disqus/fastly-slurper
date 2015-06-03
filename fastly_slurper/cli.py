"""
fastly_slurper.cli
~~~~~~~~~~~~~~~~~~

:copyright: (c) 2015 Disqus, Inc.
:license: Apache, see LICENSE for more details.
"""
import click


def make_services(ctx, param, value):
    return tuple(service.split(':', 1) for service in value)


def make_netaddr(ctx, param, value):
    if ':' not in value:
        return value, 8125

    try:
        host, port = value.rsplit(':', 1)
        return host, int(port)
    except ValueError:
        raise click.BadParameter('host needs to be of form \'IP:PORT\'')


@click.command()
@click.option('--delay', default=1.0, type=float)
@click.option('--statsd', default='localhost', callback=make_netaddr)
@click.option('--service', 'services', multiple=True, required=True, callback=make_services)
@click.option('--prefix', default='fastly')
@click.option('--api-key', required=True)
@click.option('--verbose', default=False, is_flag=True)
def slurper(delay, statsd, services, prefix, api_key, verbose):
    from .slurper import Fastly, Statsd, RecorderWorker

    client = Fastly(api_key)
    publisher = Statsd(statsd, prefix, verbose)
    for service in services:
        RecorderWorker(client, publisher, service, delay).start()

    from time import sleep
    try:
        while True:
            sleep(10)
    except KeyboardInterrupt:
        click.echo('\nbye', err=True)


def main():
    slurper(auto_envvar_prefix='SLURPER')
