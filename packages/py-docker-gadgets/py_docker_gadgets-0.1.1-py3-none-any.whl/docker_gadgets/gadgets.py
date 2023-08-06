import docker
from loguru import logger

from docker_gadgets.exceptions import DockerGadgetsError
from docker_gadgets.helpers import check_ports, cleanup_container, get_image_external, get_image_internal


def start_service(
    container_name,
    image=None,
    env=None,
    ports=None,
    volumes=None,
    command=None,
    extra_hosts=None,
    network=None,
    tmpfs=None,
):
    logger.debug(f"Starting service '{container_name}'")
    client = docker.from_env()

    if image is None:
        logger.debug(f"Retrieving internal image for {container_name}")
        image = get_image_internal(container_name)
    else:
        logger.debug(f"Retrieving external image for {container_name} using {image}")
        image = get_image_external(image)
    cleanup_container(container_name)

    if ports:
        logger.debug(f"Checking if needed ports {ports} are available")
        check_ports(ports)

    logger.debug(f"Starting container: {container_name}")
    container = client.containers.run(
        image,
        detach=True,
        name=container_name,
        command=command,
        ports=ports,
        environment=env,
        volumes=volumes,
        network=network,
        extra_hosts=extra_hosts,
        tmpfs=tmpfs,
        restart_policy=dict(Name="on-failure", MaximumRetryCount=5),
    )
    logger.debug(f"Started container: {container_name} ({container})")
    return container


def stop_service(container_name: str):
    logger.debug(f"Stopping service '{container_name}'")
    client = docker.from_env()

    logger.debug(f"Finding container '{container_name}'")
    container = client.containers.get(container_name)
    DockerGadgetsError.require_condition(
        container is not None,
        "Couldn't find a container named '{container_name}'",
    )

    DockerGadgetsError.require_condition(
        container.status == "running",
        "Container is not running",
    )
    logger.debug("Stopping container")
    container.stop()

    logger.debug(f"Stopped container: {container_name} ({container})")


def create_network(name: str):
    client = docker.from_env()
    logger.debug(f"Creating network: {name}")
    try:
        client.networks.get(name)
        logger.debug("Network is already created. Skipping")
    except docker.errors.NotFound:
        client.networks.create(name, driver="bridge")
        logger.debug(f"Created network: {name}")


# def destroy_network(name: str):
#     client = docker.from_env()
#     logger.debug(f"Destroying network: {name}")
#     # TODO: Implement this one
