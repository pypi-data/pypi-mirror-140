"""GreenDeploy is a framework that makes it easy to build Dockerized Django projects
by providing uniform templates.
"""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("greendeploy-cli")
except PackageNotFoundError:
    __version__ = "0.0.0"


import logging

logging.getLogger(__name__).addHandler(logging.NullHandler())
