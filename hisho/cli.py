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
        self.cluster = None
        self.service = None

    def setup_service(self, name):
        try:
            self.service = self.cluster.get_service(name)
        except ApiException:
            raise click.BadParameter('must pass a valid service name')

    def setup_cluster(self, name):
        try:
            self.cluster = self.api.get_cluster(name)
        except ApiException:
            raise click.BadParameter('must pass a valid cluster name')


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

    if result != 'ping':
        raise click.UsageError('successfully pinged CM, but got an unexpected result')

@click.group()
@click.option('--debug/--no-debug', default=False)
@click.pass_context
def main(ctx, debug):
    ctx.obj = Context()

    if debug:
        LOG.setLevel(logging.DEBUG)

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
    except LookupError:
        raise click.BadParameter("choose a valid encoding (got '%s')" % encoding)

    cfg = ctx.obj.config
    try:
        cfg.generate(key, num_bytes=bytes, encoding=encoding)
    except UnicodeDecodeError:
        raise click.BadParameter("could not convert value to selected encoding")
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
    pass

@click.command(name='list')
@click.pass_context
def hosts_list(ctx):
    # ensure CM is accessible
    ctx.invoke(ping)

    api = ctx.obj.api
    hosts = api.get_all_hosts().objects

    for host in hosts:
        click.echo(host.hostname)

@click.group()
@click.pass_context
def clusters(ctx):
    # ensure CM is accessible
    ctx.invoke(ping)

@click.command(name='list')
@click.pass_context
def clusters_list(ctx):

    api = ctx.obj.api
    clusters = api.get_all_clusters().objects

    for cluster in clusters:
        click.echo(cluster.name)

@click.group()
@click.pass_context
@click.option('-c', '--cluster', default=None)
def services(ctx, cluster):
    # ensure CM is accessible
    ctx.invoke(ping)

    cfg = ctx.obj.config

    cluster_name = cluster or cfg.get('cluster')
    ctx.obj.setup_cluster(cluster_name)

@click.command(name='list')
@click.pass_context
def services_list(ctx):
    api = ctx.obj.api
    cluster = ctx.obj.cluster
    services = cluster.get_all_services().objects

    for service in services:
        click.echo(service.name)

@click.group()
@click.pass_context
@click.option('-c', '--cluster', default=None)
@click.option('-s', '--service', default=None)
def roles(ctx, cluster, service):
    # ensure CM is accessible
    ctx.invoke(ping)

    cfg = ctx.obj.config

    cluster_name = cluster or cfg.get('cluster')
    service_name = service or cfg.get('service')

    ctx.obj.setup_cluster(cluster_name)
    ctx.obj.setup_service(service_name)

@click.command(name='list')
@click.pass_context
def roles_list(ctx):
    service = ctx.obj.service
    roles = service.get_all_roles().objects

    for role in roles:
        click.echo(role.name)

main.add_command(config)
main.add_command(hosts)
main.add_command(ping)
main.add_command(clusters)
main.add_command(services)
main.add_command(roles)

clusters.add_command(clusters_list)

services.add_command(services_list)

roles.add_command(roles_list)

hosts.add_command(hosts_list)

config.add_command(config_generate)
config.add_command(config_set)
config.add_command(config_rm)
config.add_command(config_show)
config.add_command(config_destroy)

if __name__ == '__main__':
    main()
