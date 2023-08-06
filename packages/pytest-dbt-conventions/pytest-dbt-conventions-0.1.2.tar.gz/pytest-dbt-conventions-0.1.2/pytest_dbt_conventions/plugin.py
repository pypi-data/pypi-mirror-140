import os
import argparse

import pytest

from artefacts.config import Config
from artefacts import Manifest, RunResults, Sources, Catalog
import artefacts.api


def pytest_addoption(parser):
    group = parser.getgroup('dbt-conventions')

    group.addoption(
        '--package-name',
        action='store',
        dest='artefacts_package_name',
        default='',
        help='The name of the dbt package to test against. Enables excluding installed packages '
             'like dbt_utils. Your package name is defined in the `dbt_project.yml` file.'
    )

    group.addoption(
        '--include-disabled',
        action='store_true',
        dest='artefacts_include_disabled',
        help='Whether to test against disabled resources.'
    )

    group.addoption(
        '--dbt-project-dir',
        action='store',
        dest='artefacts_dbt_project_dir',
        default=os.getcwd(),
        help='The filepath where the dbt project is located. Defaults to '
             'the current working directory.'
    )


def get_artefacts_config(pytest_config):
    "Setup artefacts config object based on pytest config"
    config = Config(
        dbt_project_dir=pytest_config.getoption('artefacts_dbt_project_dir')
    )
    return config


def get_api_params(pytest_config):
    "Get params to pass to `Manifest.iter_resource_type` based on pytest config"
    
    return {
        'package_name': pytest_config.getoption('artefacts_package_name'),
        'include_disabled': pytest_config.getoption('artefacts_include_disabled')
    }


resource_types = [
    'model',
    'test', 
    'seed',
    'source',
    'exposure',
    'metric',
    'macro',
    'operation',
    'snapshot',
    # 'selector',  # excluded because it needs a special parametrization function
]


def parametrize_resource_type(metafunc, resource_type, pytest_config):
    artefacts_config = get_artefacts_config(pytest_config=pytest_config)
    api_params = get_api_params(pytest_config=pytest_config)
    manifest = Manifest(config=artefacts_config)
    resources = list(manifest.iter_resource_type(resource_type, **api_params))
    
    try:
        ids = [r.unique_id for r in resources]
    except AttributeError:
        ids = list(range(len(resources)))
    
    metafunc.parametrize(resource_type, resources, ids=ids)


def parametrize_selectors(metafunc, pytest_config):
    artefacts_config = get_artefacts_config(pytest_config=pytest_config)
    manifest = Manifest(config=artefacts_config)
    selectors = manifest.selectors.values()
    ids = [s.get('name') for s in selectors]
    metafunc.parametrize('selector', selectors, ids=ids)


def pytest_generate_tests(metafunc):
    for fixture_name in metafunc.fixturenames:
        if fixture_name in resource_types:
            parametrize_resource_type(metafunc, resource_type=fixture_name, pytest_config=metafunc.config)
        elif fixture_name == 'selector':
            parametrize_selectors(metafunc, pytest_config=metafunc.config)
        else:
            continue


@pytest.fixture(scope='session')
def artefacts_config(request):
    return get_artefacts_config(request.config)


@pytest.fixture(scope='session')
def manifest(artefacts_config):
    return Manifest(config=artefacts_config)


@pytest.fixture(scope='session')
def run_results(artefacts_config):
    return RunResults(config=artefacts_config)


@pytest.fixture(scope='session')
def catalog(artefacts_config):
    return Catalog(config=artefacts_config)


@pytest.fixture(scope='session')
def sources(artefacts_config):
    return Sources(config=artefacts_config)
