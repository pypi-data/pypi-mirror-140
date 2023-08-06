import click
from FrogCli.utilities.errorHandler import error_handler
from FrogCli.utilities.repoConfig import set_repo_config

_package_types = ['alpine', 'maven', 'gradle', 'ivy', 'sbt',
                  'helm', 'rpm', 'nuget', 'cran', 'gems',
                  'npm', 'bower', 'pypi', 'docker', 'go',
                  'yum', 'chef', 'puppet', 'generic']
_rclass_types = ['local', 'remote', 'virtual']


# Create Repository
@click.command()
@click.option('--name', '--n',
              help='Please provide unique repository name',
              required=True)
@click.option('--rclass', '--rc',
              help='Please provide repository type',
              default='local',
              type=click.Choice(_rclass_types),
              show_default=True)
@click.option('--package_type', '--p',
              help='Please provide package type',
              default='generic',
              type=click.Choice(_package_types),
              show_default=True)
def create_repo(name, rclass, package_type):
    """Creates a new repository in Artifactory with the provided configuration.
    Supported by local, remote and virtual repositories"""
    route = f'artifactory/api/repositories/{name}'
    method = 'put'
    repo_config = set_repo_config(rclass, package_type)
    click.echo(f"Repository {name} will be created with rclass {rclass} and package-type {package_type}")
    confirmation = click.prompt("Answer True or False to proceed", type=bool)
    if confirmation:
        response = error_handler(method, route, repo_config)
        click.echo(response.text)
    else:
        click.echo('No action was taken')

