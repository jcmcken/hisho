import click
import urllib2
import logging
from hisho.util import Context

# root logger so we absorb log messages from ``cm_api``
LOG = logging.getLogger()

@click.command()
@click.pass_context
def ping(ctx):
    api = ctx.obj.api
    LOG.debug('pinging %s' % api.base_url)
    try:
        result = api.echo('ping').get('message')
    except urllib2.URLError:
        raise click.UsageError('could not contact CM, it may be offline')

    if result != 'ping':
        raise click.UsageError('successfully pinged CM, but got an unexpected result')

@click.group()
@click.option('--debug/--no-debug', default=False)
@click.pass_context
def main(ctx, debug):
    ctx.obj = Context()

    if debug:
        logging.basicConfig()
        LOG.setLevel(logging.DEBUG)

main.add_command(ping)
