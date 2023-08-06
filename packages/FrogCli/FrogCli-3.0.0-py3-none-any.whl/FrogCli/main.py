import click

from FrogCli.utilities.login import login
from .commands.listRepositories import get_repo_list
from .commands.systemPing import system_ping
from .commands.systemVersion import system_version
from .commands.getStorageInfo import get_storage_info
from .commands.createRepository import create_repo
from .commands.updateRepository import update_repo


@click.group()
def cli():
    login()


cli.add_command(system_ping)
cli.add_command(system_version)
cli.add_command(get_storage_info)
cli.add_command(create_repo)
cli.add_command(update_repo)
cli.add_command(get_repo_list)


if __name__ == '__main__':
    cli()

