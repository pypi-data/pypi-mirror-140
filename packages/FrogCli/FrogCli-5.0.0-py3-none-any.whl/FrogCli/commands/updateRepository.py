import click
from FrogCli.utilities.errorHandler import error_handler

_layout_types = ['bower-default', 'build-default', 'cargo-default', 'composer-default',
                 'conan-default', 'go-default', 'ivy-default']


# Update repository
@click.command()
@click.option('--name', '--n',
              help='Please provide repository name',
              required=True)
@click.option('--des', '--d',
              help='Please enter repository description',
              default='')
@click.option('--notes',
              help='Please enter repository notes',
              default='')
@click.option('--layout', '--l',
              help='Please enter repository layout',
              type=click.Choice(_layout_types))
def update_repo(name, des, notes, layout=''):
    """Updates an existing repository configuration with the provided configuration elements
    Yuo can update Repository description / notes / layout"""
    data = {}
    route = f'artifactory/api/repositories/{name}'
    method = 'post'
    if des != '':
        data['description'] = des
    elif layout != '':
        data['repoLayoutRef'] = layout
    elif notes != '':
        data['notes'] = notes
    if data == {}:
        return
    response = error_handler(method, route, data)
    if response is None or response.status_code != 200:
        return
    click.echo(response.text)


