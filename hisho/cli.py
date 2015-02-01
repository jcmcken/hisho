import codecs
import click
import logging
import urllib2
from hisho.config import Config
from cm_api.api_client import ApiResource, ApiException

LOG = logging.getLogger()

class Context(object):
    def __init__(self):
        self.config = Config()
        self.api = ApiResource(
          self.config.get('host'),
          self.config.get('port'),
          self.config.get('username'),
          self.config.get('password'),
          use_tls = self.config.get('use_tls'),
        )

@click.group()
@click.option('--debug/--no-debug', default=False)
@click.pass_context
def main(ctx, debug):
    ctx.obj = Context()

    if debug:
        LOG.setLevel(logging.DEBUG)

@click.command()
@click.pass_context
def ping(ctx):
    api = ctx.obj.api
    LOG.debug('pinging %s' % api.base_url)
    try:
        result = api.echo('ping').get('message')
    except urllib2.URLError:
        raise click.UsageError('could not contact CM, it may be offline')
    except ApiException:
        raise click.UsageError('successfully contacted CM, but the request was rejected')

    if result == 'ping':
        click.echo('OK')
    else:
        raise click.UsageError('successfully pinged CM, but got an unexpected result')

@click.group()
@click.pass_context
def config(ctx):
    pass

@click.command(name='generate')
@click.argument('key')
@click.pass_context
@click.option('--bytes', type=int, default=64)
@click.option('--encoding', default='hex')
def config_generate(ctx, key, bytes, encoding):
    try:
        codecs.lookup(encoding)
    except codecs.LookupError:
        raise click.BadParameter("invalid encoding '%s'" % encoding, param=encoding)

    cfg = ctx.obj.config
    cfg.generate(key, num_bytes=bytes, encoding=encoding)
    cfg.save()

@click.command(name='set')
@click.argument('key')
@click.argument('value')
@click.pass_context
def config_set(ctx, key, value):
    cfg = ctx.obj.config

    cfg.set(key, value)
    cfg.save()

@click.command(name='rm')
@click.argument('key')
@click.pass_context
def config_rm(ctx, key):
    cfg = ctx.obj.config

    cfg.remove(key)
    cfg.save()

@click.command(name='show')
@click.pass_context
def config_show(ctx):
    cfg = ctx.obj.config

    for k,v in cfg.iteritems():
        print k, '=', v

@click.command(name='destroy')
@click.pass_context
def config_destroy(ctx):
    cfg = ctx.obj.config
    cfg.destroy()

@click.group()
@click.pass_context
def hosts(ctx):
    click.echo('In hosts')

@click.command(name='list')
def hosts_list():
    click.echo('In hosts list')

main.add_command(config)
main.add_command(hosts)
main.add_command(ping)

hosts.add_command(hosts_list)

config.add_command(config_generate)
config.add_command(config_set)
config.add_command(config_rm)
config.add_command(config_show)
config.add_command(config_destroy)

if __name__ == '__main__':
    main()
