import click
import logging
from hisho.cli.main import ping

LOG = logging.getLogger(__name__)

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

    if not service_name:
        raise click.UsageError('must pass a service name (-s/--service)')

    ctx.obj.setup_cluster(cluster_name)
    ctx.obj.setup_service(service_name)

@click.command(name='list')
@click.pass_context
def role_list(ctx):
    service = ctx.obj.service
    roles = service.get_all_roles().objects

    for role in roles:
        click.echo(role.name)

@click.command(name='types')
@click.pass_context
def role_types(ctx):
    service = ctx.obj.service

    roles = service.get_role_types()
    roles.sort()
    
    for role in roles:
        click.echo(role)

role.add_command(role_list)
role.add_command(role_types)
