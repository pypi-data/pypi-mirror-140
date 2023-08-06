import click
from FrogCli.utilities.errorHandler import error_handler


# System Version
@click.command()
def system_version():
    """Print the system version of the Artifactory instance"""
    route = 'artifactory/api/system/version'
    method = 'get'
    response = error_handler(method, route)
    if response is None or response.status_code != 200:
        return
    click.echo(f'System Version: {response.json()["version"]}')


