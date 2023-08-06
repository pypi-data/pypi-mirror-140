import json
import click
from FrogCli.utilities.errorHandler import error_handler


# Get Storage Info
@click.command()
def get_storage_info():
    """Returns storage summary information regarding binaries, file store and repositories."""
    route = 'artifactory/api/storageinfo'
    method = 'get'
    response = error_handler(method, route)
    if response is None or response.status_code != 200:
        return
    click.echo(json.dumps(json.loads(response.text), indent=4, sort_keys=True))



