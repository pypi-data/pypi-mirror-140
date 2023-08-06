"""
This module implements a simple API for launching a swagger UI for trying out a HEA microservice's REST APIs.
"""
import logging

from testcontainers.mongodb import MongoDbContainer
from contextlib import ExitStack
from . import runner, wstl, db
from .db import mongo
from aiohttp_swagger3 import SwaggerDocs, SwaggerUiSettings
from aiohttp_swagger3.handlers import application_json
from aiohttp import web
from importlib.metadata import version
from typing import Dict, List, Tuple, Callable, Iterable, Optional
from types import ModuleType
import os
from .docker import get_exposed_port, DockerImages
from heaserver.service.docker import DockerContainerSpec, start_microservice_container
from heaobject.root import HEAObjectDict
from copy import deepcopy

from .openapi import download_openapi_spec


def run(project_slug: str,
        fixtures: Dict[str, List[HEAObjectDict]],
        module: ModuleType,
        routes: Iterable[Tuple[Callable, str, Callable]],
        registry_docker_image: Optional[str] = None,
        other_docker_images: Optional[List[DockerContainerSpec]] = None) -> None:
    """
    Launches a swagger UI for trying out the given HEA APIs. It downloads the HEA OpenAPI spec from gitlab.com. It
    launches Docker containers for any other projects specified in the other_docker_images argument. It also
    launches two MongoDB databases in Docker containers, one for the project being tested, and the other for the other
    containers. It inserts the given HEA objects into both databases, creates HEA Server Registry entries for all
    containers, and makes the given routes available to query in swagger. All containers run on Docker's default bridge
    network.

    This function creates two MongoDB databases because the project being tested is not running in a Docker container,
    so it needs any other containers' external URLs (starting with localhost) rather than Docker's internal network's
    IP addresses. To simplify this function's arguments, we load the exact same data into both MongoDB databases,
    except for the registry components, which differ only in their base URLs and names. The latter is set to the
    component's base URL. One of the databases will contain localhost base URLs, and the other will contain Docker
    bridge network IP addresses. This function logs each MongoDB container's mongo connection string at the info level
    so that you can tell which container is which.

    :param project_slug: the Gitlab project slug of interest. Required.
    :param fixtures: a mapping of mongo collection -> list of HEA objects as dicts. Required.
    :param module: the microservice's service module.
    :param routes: a list of three-tuples containing the command, path and collable of each route of interest. The
    commands are one of: aiohttp.web.get, aiohttp.web.delete, aiohttp.web.post, aiohttp.web.put or aiohttp.web.view.
    :param registry_docker_image: an heaserver-registry docker image in REPOSITORY:TAG format, that will be launched
    after the MongoDB container is live.
    :param other_docker_images: optional list of ContainerSpec objects, which specify additional HEA microservice
    Docker containers to start.
    :raises OSError: If an error occurred accessing the OpenAPI spec.
    """
    if other_docker_images and registry_docker_image is None:
        raise ValueError('registry_docker_image must be non-None when other_docker_images is not empty')

    bridge_fixtures, external_fixtures = deepcopy(fixtures), deepcopy(fixtures)
    os.environ['MONGO_DB'] = 'hea'
    logger = logging.getLogger(__name__)
    with ExitStack() as stack, download_openapi_spec() as open_api_spec_file:
        external_mongo, external_mongodb_connection_string = _start_mongo(stack)
        logger.info('Mongo for the project being tested has connection string %s', external_mongodb_connection_string)

        if other_docker_images or registry_docker_image is not None:
            bridge_mongo, bridge_mongodb_connection_string = _start_mongo(stack)
        else:
            bridge_mongo = None
            bridge_mongodb_connection_string = None

        if registry_docker_image is not None:
            _, bridge_registry_url = start_microservice_container(
                DockerContainerSpec(image=registry_docker_image, port=8080, check_path='/components'), bridge_mongo,
                stack)
            external_registry_url, _ = start_microservice_container(
                DockerContainerSpec(image=registry_docker_image, port=8080, check_path='/components'), external_mongo,
                stack)
        else:
            external_registry_url = None
            bridge_registry_url = None

        if other_docker_images:
            logger.info('Bridge mongo for any other projects has connection string %s',
                        bridge_mongodb_connection_string)
            _start_other_docker_containers(bridge_fixtures, external_fixtures, bridge_mongo, other_docker_images,
                                           bridge_registry_url, stack)
            _insert_fixtures_into_db(bridge_mongo, bridge_fixtures)

        _start_project(external_fixtures, external_mongo, external_mongodb_connection_string, external_registry_url,
                       module, open_api_spec_file, project_slug, routes)


def _start_project(external_fixtures, external_mongo, external_mongodb_connection_string, external_registry_url, module,
                   open_api_spec_file, project_slug, routes):
    config_file = _generate_config_file(external_mongodb_connection_string, external_registry_url)
    config = runner.init(config_string=config_file)
    _insert_fixtures_into_db(external_mongo, external_fixtures)
    app = runner.get_application(db.mongo.Mongo,
                                 wstl_builder_factory=wstl.builder_factory(module.__package__, href='/'),
                                 config=config)
    _init_swagger_docs(app, open_api_spec_file, project_slug, routes)
    web.run_app(app)


def _start_other_docker_containers(bridge_fixtures: Dict[str, List[HEAObjectDict]],
                                   external_fixtures: Dict[str, List[HEAObjectDict]], mongo_: MongoDbContainer,
                                   other_docker_images: Optional[List[DockerContainerSpec]],
                                   registry_url: Optional[str], stack: ExitStack):
    for img in other_docker_images or []:
        external_url, bridge_url = start_microservice_container(img, mongo_, stack, registry_url)
        bridge_fixtures.setdefault('components', []).append(
            {'type': 'heaobject.registry.Component', 'base_url': bridge_url, 'name': bridge_url,
             "owner": "system|none",
             'resources': [r.to_dict() for r in img.resources or []]})
        external_fixtures.setdefault('components', []).append(
            {'type': 'heaobject.registry.Component', 'base_url': external_url, 'name': external_url,
             "owner": "system|none",
             'resources': [r.to_dict() for r in img.resources or []]})


def _init_swagger_docs(app: web.Application, openapi_spec_file: Optional[str], project_slug: str,
                       routes: Iterable[Tuple[Callable, str, Callable]]) -> None:
    swagger = SwaggerDocs(app,
                          swagger_ui_settings=SwaggerUiSettings(path="/docs"),
                          title=project_slug,
                          version=version(project_slug),
                          components=openapi_spec_file)
    swagger.register_media_type_handler('application/vnd.collection+json', application_json)
    swagger.add_routes([r[0](r[1], r[2]) for r in routes])


def _generate_config_file(mongodb_connection_string: str, registry_url: Optional[str]) -> str:
    if registry_url is None:
        config_file = f"""
[MongoDB]
ConnectionString = {mongodb_connection_string}
"""
    else:
        config_file = f"""
[DEFAULT]
Registry={registry_url}

[MongoDB]
ConnectionString = {mongodb_connection_string}
                """
    return config_file


def _start_mongo(stack: ExitStack) -> Tuple[MongoDbContainer, str]:
    mongo_container = MongoDbContainer(DockerImages.MONGODB.value)
    mongo_ = stack.enter_context(mongo_container)
    mongodb_connection_string = f'mongodb://test:test@{mongo_.get_container_host_ip()}:{get_exposed_port(mongo_, 27017)}/hea?authSource=admin'
    return mongo_, mongodb_connection_string


def _insert_fixtures_into_db(mongo_: MongoDbContainer, fixtures: Dict[str, List[HEAObjectDict]]) -> None:
    db_ = mongo_.get_connection_client().hea
    for k in fixtures or {}:
        db_[k].insert_many(mongo.replace_id_with_object_id(f) for f in fixtures[k])
