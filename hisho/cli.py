import types
import codecs
import click
import logging
import urllib2
from functools import wraps
from hisho.config import Config, DEFAULTS
from cm_api.api_client import ApiResource, ApiException

LOG = logging.getLogger()

def api_wrapper(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
        except ApiException, e:
            LOG.exception('got API exception')
            raise click.UsageError('API command failed, use --debug to see more information')
        return result
    return wrapper

class APIWrapper(object):
    def __init__(self, api_resource):
        self.api_resource = api_resource

    def __getattr__(self, name):
        obj = getattr(self.api_resource, name)

        if isinstance(obj, (types.MethodType, types.FunctionType)):
            result = api_wrapper(obj)
        else:
            result = obj
        return result

class Context(object):
    def __init__(self):
        self.config = Config()
        self.api = APIWrapper(ApiResource(
          self.config.get('host'),
          self.config.get('port'),
          self.config.get('username'),
          self.config.get('password'),
          use_tls = self.config.get('use_tls'),
        ))
        self.cluster = None
        self.service = None

    def setup_service(self, name):
        self.service = APIWrapper(self.cluster.get_service(name))

    def setup_cluster(self, name):
        self.cluster = APIWrapper(self.api.get_cluster(name))

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
def host(ctx):
    pass

@click.command(name='list')
@click.pass_context
def host_list(ctx):
    # ensure CM is accessible
    ctx.invoke(ping)

    api = ctx.obj.api
    hosts = api.get_all_hosts().objects

    import pdb;pdb.set_trace()

    for host in hosts:
        click.echo(host.hostname)

@click.group()
@click.pass_context
def cluster(ctx):
    # ensure CM is accessible
    ctx.invoke(ping)

@click.command(name='list')
@click.pass_context
def cluster_list(ctx):

    api = ctx.obj.api
    clusters = api.get_all_clusters().objects

    for cluster in clusters:
        click.echo(cluster.name)

@click.command(name='create')
@click.pass_context
@click.argument('cluster_name')
@click.argument('full_version')
def cluster_create(ctx, cluster_name, full_version):
    api = ctx.obj.api

    api.create_cluster(cluster_name, fullVersion=full_version)

@click.command(name='rm')
@click.pass_context
@click.argument('cluster_name')
def cluster_rm(ctx, cluster_name):
    api = ctx.obj.api

    api.delete_cluster(cluster_name)

@click.group()
@click.pass_context
@click.option('-c', '--cluster', default=None)
def service(ctx, cluster):
    # ensure CM is accessible
    ctx.invoke(ping)

    cfg = ctx.obj.config

    cluster_name = cluster or cfg.get('cluster')
    ctx.obj.setup_cluster(cluster_name)

@click.command(name='list')
@click.pass_context
def service_list(ctx):
    api = ctx.obj.api
    cluster = ctx.obj.cluster
    services = cluster.get_all_services().objects

    for service in services:
        click.echo(service.name)

@click.group()
@click.pass_context
@click.option('-c', '--cluster', default=None)
@click.option('-s', '--service', default=None)
def role(ctx, cluster, service):
    # ensure CM is accessible
    ctx.invoke(ping)

    cfg = ctx.obj.config

    cluster_name = cluster or cfg.get('cluster')
    service_name = service or cfg.get('service')

    ctx.obj.setup_cluster(cluster_name)
    ctx.obj.setup_service(service_name)

@click.command(name='list')
@click.pass_context
def role_list(ctx):
    service = ctx.obj.service
    roles = service.get_all_roles().objects

    for role in roles:
        click.echo(role.name)

main.add_command(config)
main.add_command(host)
main.add_command(ping)
main.add_command(cluster)
main.add_command(service)
main.add_command(role)

cluster.add_command(cluster_list)
cluster.add_command(cluster_create)
cluster.add_command(cluster_rm)

service.add_command(service_list)

role.add_command(role_list)

host.add_command(host_list)

config.add_command(config_generate)
config.add_command(config_set)
config.add_command(config_rm)
config.add_command(config_show)
config.add_command(config_destroy)

if __name__ == '__main__':
    main()
