# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['docker_gadgets']

package_data = \
{'': ['*']}

install_requires = \
['docker>=5.0.3,<6.0.0', 'loguru>=0.6.0,<0.7.0', 'py-buzz>=3.0.0,<4.0.0']

setup_kwargs = {
    'name': 'py-docker-gadgets',
    'version': '0.1.1',
    'description': 'Some convenience tools for managing docker containers in python',
    'long_description': '.. image::  https://badge.fury.io/py/py-docker-gadgets.svg\n   :target: https://badge.fury.io/py/py-docker-gadgets\n   :alt:    Latest Version\n\n*****************\n py-docker-tools\n*****************\n\n-----------------------------------------------------------------\n Some convenience tools for managing docker containers in python\n-----------------------------------------------------------------\n\npy-docker-gadgets is a very compact set of tools for working with docker containers in python. Its API exposes\na very simple command to spin up a container and then shut it down.\n\n\nSuper Quick Start\n-----------------\n\n - requirements: `python3`\n - install through pip: `$ pip install py-docker-tools`\n\nExample Usage\n-------------\n\nHere\'s a very basic example of how this could be used:\n\n.. code-block:: python\n\n   from docker_gadgets import start_service, stop_service\n\n   start_service(\n       "test-postgres",\n       image="postgres",\n       env=dict(\n           POSTGRES_PASSWORD="test-password",\n           POSTGRES_USER="test-user",\n           POSTGRES_DB="test-db",\n       ),\n       ports={"5432/tcp": 8432},\n   )\n   stop_service("test-postgres")\n',
    'author': 'Tucker Beck',
    'author_email': 'tucker.beck@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
