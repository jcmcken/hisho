import click
import logging
from hisho.cli.main import ping

LOG = logging.getLogger(__name__)

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

cluster.add_command(cluster_list)
cluster.add_command(cluster_create)
cluster.add_command(cluster_rm)
