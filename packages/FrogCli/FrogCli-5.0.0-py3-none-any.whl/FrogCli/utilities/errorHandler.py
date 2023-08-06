import importlib
import json
import click
import requests
from FrogCli.utilities.api_config import HEADERS, API_URL


def error_handler(method, route, data={}):
    response = None
    try:
        if method == 'get':
            response = requests.get(f'{API_URL}{route}',
                                    headers=HEADERS)
        elif method == 'put':
            response = requests.put(f'{API_URL}{route}',
                                    headers=HEADERS,
                                    data=json.dumps(data))
        elif method == 'post':
            response = requests.post(f'{API_URL}{route}',
                                     headers=HEADERS,
                                     data=json.dumps(data))
        if response.status_code == 400:
            print(f"Error msg from instance: {response.json()['errors'][0]['message']}")
        response.raise_for_status()
        click.echo(f'Status code: {response.status_code}')

        return response
    except requests.exceptions.HTTPError as errh:
        print(errh)
    except requests.exceptions.ConnectionError as errc:
        print(errc)
    except requests.exceptions.Timeout as errt:
        print(errt)
    except requests.exceptions.RequestException as err:
        print(err)

