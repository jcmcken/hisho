import click
import logging

LOG = logging.getLogger(__name__)

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

config.add_command(config_generate)
config.add_command(config_set)
config.add_command(config_rm)
config.add_command(config_show)
config.add_command(config_destroy)
