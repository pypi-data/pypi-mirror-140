"""
Utility functions and classes for working with docker images and containers.
"""
from contextlib import ExitStack

from testcontainers.general import DockerContainer
from testcontainers.core.waiting_utils import wait_container_is_ready
import requests
from testcontainers.mongodb import MongoDbContainer
from yarl import URL
from typing import Dict, List, Tuple
from copy import deepcopy, copy
from typing import Optional
import logging
from heaobject.registry import Resource
from enum import Enum


class DockerImages(Enum):
    """
    Images to use for SwaggerUI, tests, and other situations in which we want HEA to start Docker containers
    automatically.
    """
    MONGODB = 'percona/percona-server-mongodb:4.4.9'


class DockerVolumeMapping:
    """
    Docker volume mapping. This class is immutable.
    """

    def __init__(self, host: str, container: str, mode: str = 'ro'):
        """
        Creates a volume mapping.

        :param host: the path of the directory on the host to map (required).
        :param container: the path to mount the volume in the container (required).
        :param mode: access level in the container as Unix rwx-style permissions (defaults to 'ro').
        """
        if mode is None:
            self.__mode: str = 'ro'
        else:
            self.__mode = str(mode)
        self.__container = str(container)
        self.__host = str(host)

    @property
    def host(self) -> str:
        return self.__host

    @property
    def container(self) -> str:
        return self.__container

    @property
    def mode(self) -> str:
        return self.__mode


class DockerContainerSpec:
    """
    Docker image and configuration for starting a container. This class is immutable.
    """

    def __init__(self, image: str, port: int, check_path: Optional[str] = None,
                 resources: Optional[List[Resource]] = None,
                 volumes: Optional[List[DockerVolumeMapping]] = None,
                 env_vars: Optional[Dict[str, str]] = None):
        """
        Constructor.

        :param image: the image tag (required).
        :param port: the exposed port (required).
        :param check_path: the URL path to check if the microservice is running.
        :param resources: a list of heaobject.registry.Resource dicts indicating what content types this image is designed for.
        :param volumes: a list of volume mappings.
        :param env_vars: a dict containing environment variable names mapped to string values.
        """
        if image is None:
            raise ValueError('image cannot be None')
        if port is None:
            raise ValueError('port cannot be None')
        if any(not isinstance(volume, DockerVolumeMapping) for volume in volumes or []):
            raise TypeError(f'volumes must contain only {DockerVolumeMapping} objects')
        if any(not isinstance(k, str) and isinstance(v, str) for k, v in (env_vars or {}).items()):
            raise TypeError('env_vars must be a str->str dict')
        if any(not isinstance(r, Resource) for r in resources or []):
            raise TypeError(f'resources must contain only {Resource} objects')
        self.__image = str(image)
        self.__port = int(port)
        self.__check_path = str(check_path)
        self.__resources = [deepcopy(e) for e in resources or []]
        self.__volumes = list(volumes) if volumes else []
        self.__env_vars = dict(env_vars) if env_vars is not None else {}

    @property
    def image(self) -> str:
        """
        The image tag (read-only).
        """
        return self.__image

    @property
    def port(self) -> int:
        """
        The exposed port (read-only).
        """
        return self.__port

    @property
    def check_path(self) -> Optional[str]:
        """
        The URL path to check for whether the microservice is running (read-only).
        """
        return self.__check_path

    @property
    def resources(self) -> Optional[List[Resource]]:
        """
        A list of heaobject.registry.Resource dicts indicating what content types this image is designed for (read-only).
        """
        return deepcopy(self.__resources)

    @property
    def volumes(self) -> List[DockerVolumeMapping]:
        """
        A list of VolumeMapping instances indicating what volumes to map (read-only, never None).
        """
        return copy(self.__volumes)

    @property
    def env_vars(self) -> Dict[str, str]:
        """
        A dict of environment variable names to string values.
        """
        return copy(self.__env_vars)

    def start(self, stack: ExitStack) -> DockerContainer:
        """
        Start a container using this image, port number, and volume mappings, connecting to the provided MongoDB
        container for database access, and using the provided HEA Server Registry instance.

        :param mongo_: the MongoDB container to use (required).
        :param registry_url: the URL of the registry service to use (optional).
        :param stack: the ExitStack to use (required).
        :return: itself, but started.
        """
        container = DockerContainer(self.image)
        for env, val in self.env_vars.items():
            container.with_env(env, val)
        for volume in self.volumes:
            container.with_volume_mapping(volume.host, volume.container, volume.mode)
        container.with_exposed_ports(self.port)
        microservice = stack.enter_context(container)
        return microservice

    def with_env_vars(self, env_vars: Dict[str, str]) -> 'DockerContainerSpec':
        """
        Returns a new DockerContainerSpec with the same values as this one, plus any environment variables in the
        env_vars argument.

        :param env_vars: any environment variables.
        :return:
        """
        new_env_vars = self.env_vars
        new_env_vars.update(env_vars)
        return DockerContainerSpec(self.image, self.port, self.check_path, self.resources, self.volumes, new_env_vars)


@wait_container_is_ready()
def get_exposed_port(container: DockerContainer, port: int) -> int:
    """
    Returns the actual port that the docker container is listening to. It tries getting the port repeatedly until the
    container has sufficiently started to assign the port number.

    :param container: the docker container (required).
    :param port: the port to which the container's application is listening internally.
    :return: the exposed port.
    """
    return container.get_exposed_port(port)


@wait_container_is_ready()
def wait_for_status_code(url, status: int):
    """
    Makes a HTTP GET call to the provided URL repeatedly until the returned status code is equal to the provided code.

    :param url: the URL to call.
    :param status: the status code to check for.
    """
    actual_status = requests.get(url).status_code
    if actual_status != status:
        raise ValueError(f'Expected status {status} and actual status {actual_status}')


@wait_container_is_ready()
def get_bridge_ip(container: DockerContainer) -> str:
    """
    Returns the IP address of the container on the default bridge network.
    :param container: a docker container.
    :return: an IP address.
    """
    return container.get_docker_client().bridge_ip(container.get_wrapped_container().id)


def start_microservice_container(container_spec: DockerContainerSpec, mongo_: MongoDbContainer, stack: ExitStack,
                                 registry_url: Optional[str] = None,
                                 mongo_hea_database: Optional[str] = 'hea',
                                 mongo_hostname: Optional[str] = None,
                                 mongo_hea_username: Optional[str] = 'test',
                                 mongo_hea_password: Optional[str] = 'test') -> Tuple[str, str]:
    """
    Starts a Docker container with the provided HEA microservice image and configuration (container_spec argument),
    Mongo database container, and exit stack for cleaning up resources. If the docker_image object has a check_path,
    the function will wait until the microservice returns a 200 status code from a GET call to the path before
    returning a two-tuple with the container's external and bridge URLs. This function wraps DockerImage's start()
    method.

    The following environment variables are set in the container and will overwrite any pre-existing values that were
    set using the image's env_vars property:
        MONGO_HEA_DATABASE is set to the value of the hea_database argument.
        HEASERVER_REGISTRY_URL is set to the value of the registry_url argument.
        MONGO_HOSTNAME is set to the value of the mongo_hostname argument.
        MONGO_HEA_DATABASE is set to the value of the mongo_hea_database argument.
        MONGO_HEA_USERNAME is set to the value of the mongo_hea_username argument.
        MONGO_HEA_PASSWORD is set to the value of the mongo_hea_password argument.

    Any other environment variables set using the image's env_vars property are retained.

    :param container_spec: the Docker image to start (required).
    :param mongo_: the MongoDBContainer (required)
    :param stack: the ExitStack (required).
    :param registry_url: optional base URL for the heaserver-registry microservice.
    :param mongo_hea_database: optional MongoDB database name to use. The default is 'hea'.
    :param mongo_hostname: optional MongoDB hostname. If None, the bridge IP address of the provided MongoDB container
    is used.
    :param mongo_hea_username: username for accessing the database. The default is 'test'.
    :param mongo_hea_password: password for accessing the database. The default is 'test'.
    :return: a two-duple containing the container's external URL string and the bridge URL string.
    """
    logger = logging.getLogger(__name__)
    logger.debug('Starting docker container %s', container_spec.image)
    image_ = copy(container_spec)
    if mongo_hea_database is None:
        mongo_hea_database = 'hea'
    if mongo_hea_username is None:
        mongo_hea_username = 'test'
    if mongo_hea_password is None:
        mongo_hea_password = 'test'
    if mongo_hostname is None:
        mongo_hostname = get_bridge_ip(mongo_)
    image_ = _with_hea_env_vars(image_, registry_url, mongo_hostname, mongo_hea_database, mongo_hea_username, mongo_hea_password)

    microservice = image_.start(stack)

    external_url = f'http://{microservice.get_container_host_ip()}:{get_exposed_port(microservice, image_.port)}'
    logger.debug('External URL of docker image %s is %s', image_.image, external_url)

    if image_.check_path is not None:
        wait_for_status_code(str(URL(external_url).with_path(image_.check_path)), 200)

    bridge_url = f'http://{get_bridge_ip(microservice)}:{image_.port}'
    logger.debug('Internal URL of docker image %s is %s', image_.image, bridge_url)

    return external_url, bridge_url


def _with_hea_env_vars(container_spec: DockerContainerSpec, registry_url: Optional[str], mongo_hostname: Optional[str],
                       mongo_hea_database: Optional[str],
                       mongo_hea_username: Optional[str], mongo_hea_password: Optional[str]) -> DockerContainerSpec:
    """
    Copies the provided container_spec, adding the environment variables corresponding to the provided arguments.

    :param container_spec: the image and configuration.
    :param registry_url: the URL of the registry service, which populates the HEASERVER_REGISTRY_URL environment
    variable.
    :param mongo_hostname: the hostname of the MongoDB service, which populates the MONGO_HOSTNAME environment variable.
    :param mongo_hea_database: the MongoDB database name, which populates the MONGO_HEA_DATABASE environment variable.
    :param mongo_hea_username: the MongoDB username, which populates the MONGO_HEA_USERNAME environment variable.
    :param mongo_hea_password: the MongoDB password, which populates the MONGO_HEA_PASSWORD environment variable.
    :return: the copy of the provided container_spec.
    """
    env_vars: Dict[str, str] = {}
    if mongo_hea_database is not None:
        env_vars['MONGO_HEA_DATABASE'] = mongo_hea_database
    if mongo_hea_username is not None:
        env_vars['MONGO_HEA_USERNAME'] = mongo_hea_username
    if mongo_hea_password is not None:
        env_vars['MONGO_HEA_PASSWORD'] = mongo_hea_password
    if registry_url is not None:
        env_vars['HEASERVER_REGISTRY_URL'] = registry_url
    if mongo_hostname is not None:
        env_vars['MONGO_HOSTNAME'] = mongo_hostname
    return container_spec.with_env_vars(env_vars)
