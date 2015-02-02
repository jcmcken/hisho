from hisho.cli.main import main, ping
from hisho.cli.config import config
from hisho.cli.cluster import cluster
from hisho.cli.host import host
from hisho.cli.role import role
from hisho.cli.service import service

# wire up subcommands
main.add_command(config)
main.add_command(host)
main.add_command(cluster)
main.add_command(service)
main.add_command(role)
