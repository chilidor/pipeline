import httpx
import pytest

from pipeline import configuration
from pipeline.console import main as cli_main
from pipeline.console.environments import (
    _add_packages_to_environment,
    _create_environment,
    _delete_environment,
    _get_environment,
    _list_environments,
    _remove_packages_from_environment,
    _update_environment_lock,
)
from pipeline.schemas.environment import EnvironmentCreate, EnvironmentGet
from pipeline.schemas.pagination import Paginated


def _set_testing_remote_compute_service(url, token):
    cli_main(["remote", "login", "-u", url, "-t", token])
    cli_main(["remote", "set", url])
    configuration.DEFAULT_REMOTE = url


@pytest.mark.usefixtures("top_api_server")
def test_cli_environments_get(
    environment_get: EnvironmentGet,
    url: str,
    token: str,
):
    _set_testing_remote_compute_service(url, token)
    assert environment_get == _get_environment(environment_get.name)
    assert environment_get == _get_environment(environment_get.id)

    with pytest.raises(httpx.HTTPStatusError):
        _get_environment("missing_environment")


@pytest.mark.usefixtures("top_api_server")
def test_cli_environments_create(
    environment_create: EnvironmentCreate,
    environment_get: EnvironmentGet,
    url: str,
    token: str,
):
    _set_testing_remote_compute_service(url, token)
    assert environment_get == _create_environment(
        name=environment_create.name, packages=environment_create.python_requirements
    )


@pytest.mark.usefixtures("top_api_server")
def test_cli_environments_delete(
    environment_get: EnvironmentGet,
    url: str,
    token: str,
):
    _set_testing_remote_compute_service(url, token)
    _delete_environment(environment_get.name)
    _delete_environment(environment_get.id)

    with pytest.raises(httpx.HTTPStatusError):
        _delete_environment("missing_environment")


@pytest.mark.usefixtures("top_api_server")
def test_cli_environments_update(
    environment_get: EnvironmentGet,
    environment_get_add_package: EnvironmentGet,
    environment_get_rm_package: EnvironmentGet,
    url: str,
    token: str,
):

    # locking
    _set_testing_remote_compute_service(url, token)
    assert _update_environment_lock(environment_get.id, locked=True).locked

    # deps
    assert (
        _add_packages_to_environment(
            environment_get.id, ["dependency_3"]
        ).python_requirements
        == environment_get_add_package.python_requirements
    )
    assert (
        _remove_packages_from_environment(
            environment_get.id, ["dependency_1"]
        ).python_requirements
        == environment_get_rm_package.python_requirements
    )


@pytest.mark.usefixtures("top_api_server")
def test_cli_environments_list(
    environment_get: EnvironmentGet,
    environment_get_add_package: EnvironmentGet,
    environment_get_rm_package: EnvironmentGet,
    url: str,
    token: str,
):
    _set_testing_remote_compute_service(url, token)

    assert Paginated[EnvironmentGet](
        skip=1,
        limit=3,
        total=4,
        data=[
            environment_get,
            environment_get_add_package,
            environment_get_rm_package,
        ],
    ) == _list_environments(skip=1, limit=3)
