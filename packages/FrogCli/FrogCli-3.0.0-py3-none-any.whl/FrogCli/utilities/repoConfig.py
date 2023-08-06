import click


def set_repo_config(rclass, package_type):
    config_obj = {'rclass': rclass, 'packageType': package_type}
    if rclass == 'remote' or rclass == 'virtual':
        config_obj['externalDependenciesEnabled'] = False
        if rclass == 'remote':
            config_obj['url'] = click.prompt("Please enter remote url")
    return dict(config_obj)

