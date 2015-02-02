import click
import logging
from hisho.cli.main import ping

LOG = logging.getLogger(__name__)

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

@click.command(name='types')
@click.pass_context
def service_types(ctx):
    api = ctx.obj.api
    cluster = ctx.obj.cluster
    services = cluster.get_service_types()
    services.sort()

    for service in services:
        click.echo(service)

@click.command(name='create')
@click.pass_context
@click.argument('service_type')
def service_create(ctx, service_type):
    api = ctx.obj.api
    cluster = ctx.obj.cluster

    cluster.create_service(service_type.lower(), service_type.upper())

@click.command(name='rm')
@click.pass_context
@click.argument('service_name')
def service_rm(ctx, service_name):
    api = ctx.obj.api
    cluster = ctx.obj.cluster

    cluster.delete_service(service_name)

service.add_command(service_list)
service.add_command(service_types)
service.add_command(service_create)
service.add_command(service_rm)
