import click
from FrogCli.utilities.errorHandler import error_handler

_repo_types = ['local', 'remote', 'virtual']


# List repositories
@click.command()
@click.option('--repo_type', '--t',
              help='You can search by Repository type',
              type=click.Choice(_repo_types))
def get_repo_list(repo_type=None):
    """Returns a list of minimal repository details."""
    route = f'artifactory/api/repositories'
    method = 'get'
    if repo_type is not None:
        route = route + f'?type={repo_type}'
    response = error_handler(method, route)
    if response is None or response.status_code != 200:
        return
    click.echo(response.text)
