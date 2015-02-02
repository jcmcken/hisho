import click
import logging

LOG = logging.getLogger(__name__)

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

    for host in hosts:
        click.echo(host.hostname)

host.add_command(host_list)
