.. image::  https://badge.fury.io/py/py-docker-gadgets.svg
   :target: https://badge.fury.io/py/py-docker-gadgets
   :alt:    Latest Version

*****************
 py-docker-tools
*****************

-----------------------------------------------------------------
 Some convenience tools for managing docker containers in python
-----------------------------------------------------------------

py-docker-gadgets is a very compact set of tools for working with docker containers in python. Its API exposes
a very simple command to spin up a container and then shut it down.


Super Quick Start
-----------------

 - requirements: `python3`
 - install through pip: `$ pip install py-docker-tools`

Example Usage
-------------

Here's a very basic example of how this could be used:

.. code-block:: python

   from docker_gadgets import start_service, stop_service

   start_service(
       "test-postgres",
       image="postgres",
       env=dict(
           POSTGRES_PASSWORD="test-password",
           POSTGRES_USER="test-user",
           POSTGRES_DB="test-db",
       ),
       ports={"5432/tcp": 8432},
   )
   stop_service("test-postgres")
