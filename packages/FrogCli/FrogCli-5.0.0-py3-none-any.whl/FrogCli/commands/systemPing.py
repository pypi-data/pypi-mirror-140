import click
from FrogCli.utilities.errorHandler import error_handler
import os


# System Ping
@click.command()
@click.option('--ip',
              default='0.0.0.0',
              help='You can provide other ip/host name to ping for it')
def system_ping(ip):
    """Sends a ping request to the instance or a given ip/host name"""
    if ip != '0.0.0.0':
        os.system('ping ' + ip)
        return
    route = 'access/api/v1/system/ping'
    method = 'get'
    response = error_handler(method, route)
    if response is None or response.status_code != 200:
        return
    click.echo(f'Content: {response.text}')

