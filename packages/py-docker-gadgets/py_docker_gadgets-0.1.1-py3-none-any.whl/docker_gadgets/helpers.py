import errno
import socket

import docker
from loguru import logger

from docker_gadgets.exceptions import DockerGadgetsError


def cleanup_container(container_name):
    client = docker.from_env()
    try:
        logger.debug(f"Checking for existing container: {container_name}")
        container = client.containers.get(container_name)
        logger.debug(f"Cleaning up before running container: {container_name}")

        if container.status == "running":
            logger.debug(f"Stopping active container: {container_name}")
            container.stop()

        logger.debug(f"Removing existing container: {container_name}")
        container.remove()
    except docker.errors.NotFound:
        logger.debug(f"No existing container found: {container_name}")


def get_image_internal(container_name):
    client = docker.from_env()

    logger.debug(f"Looking for {container_name} image")
    with DockerGadgetsError.handle_errors(
        f"Couldn't find image matching {container_name}. Have you built this yet?",
    ):
        image = client.images.get(container_name)
    logger.debug(f"Found {container_name} image with tags: {image.tags}")
    return image


def get_image_external(image):
    client = docker.from_env()
    (repository, *rest) = image.split(":")
    tag = rest[0] if len(rest) > 0 else None
    logger.debug(f"Pulling {image} image ({tag=})")
    return client.images.pull(repository, tag=tag)


def sys_port_open(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as test_socket:
        try:
            test_socket.bind(("127.0.0.1", int(port)))
            return True
        except socket.error as err:
            if err.errno == errno.EADDRINUSE:
                return False
            else:
                logger.error(f"Unknown port problem: {str(err)}")
                raise


def check_ports(ports):
    client = docker.from_env()
    with DockerGadgetsError.check_expressions("Some required ports are already being used") as check:
        for (_, host_port) in ports.items():
            check(
                sys_port_open(host_port),
                f"Port {host_port} is being used something else on the system",
            )
            for container in client.containers.list():
                check(
                    host_port not in container.ports,
                    f"Port {host_port} is being used by container {container}",
                )
