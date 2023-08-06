"""greendeploy is a CLI for managing Dockerized Django projects.
This module implements commands available from the greendeploy CLI.
"""
import importlib
from pathlib import Path
from typing import Any, Sequence

import click
from click.utils import get_os_args
from greendeploy import __version__ as version
from greendeploy.framework.cli.starters import create_cli
from greendeploy.framework.cli.utils import (CONTEXT_SETTINGS,
                                             CommandCollection,
                                             load_entry_points)
from pyfiglet import figlet_format

FIGLET_LOGO = figlet_format("GreenDeploy", font="slant")

LOGO_WITH_VERSION = FIGLET_LOGO + f"\nv{version}"

@click.group(context_settings=CONTEXT_SETTINGS, name="GreenDeploy")
@click.version_option(version, "--version", "-V", help="Show version and exit")
def cli():  # pragma: no cover
    """GreenDeploy is a CLI for creating and using Dockerized Django projects. For more
    information, type ``greendeploy info``.
    When inside a Dockerized Django project (created with ``greendeploy new``) commands from
    the project's ``cli.py`` file will also be available here.
    """
    pass

@cli.command()
def info():
    """Get more information about GreenDeploy."""
    click.secho(LOGO_WITH_VERSION, fg="green")
    click.echo(
        "GreenDeploy is a Python framework for\n"
        "creating reproducible, maintainable\n"
        "and modular Dockerized Django projects.\n"
    )


class GreenDeployCLI(CommandCollection):
    """A CommandCollection class to encapsulate the GreenDeployCLI command
    loading.
    """

    def __init__(self, project_path: Path):
        self._metadata = None  # running in package mode
        # if _is_project(project_path):
        #     self._metadata = bootstrap_project(project_path)
        # self._cli_hook_manager = get_cli_hook_manager()

        super().__init__(
            ("Global commands", self.global_groups),
            # ("Project specific commands", self.project_groups),
        )

    def main(
        self,
        args=None,
        prog_name=None,
        complete_var=None,
        standalone_mode=True,
        **extra,
    ):
        if self._metadata:
            extra.update(obj=self._metadata)

        # This is how click's internals parse sys.argv, which include the command,
        # subcommand, arguments and options. click doesn't store this information anywhere
        # so we have to re-do it.
        # https://github.com/pallets/click/blob/main/src/click/core.py#L942-L945
        args = get_os_args() if args is None else list(args)
        # self._cli_hook_manager.hook.before_command_run(  # pylint: disable=no-member
        #     project_metadata=self._metadata, command_args=args
        # )

        super().main(
            args=args,
            prog_name=prog_name,
            complete_var=complete_var,
            standalone_mode=standalone_mode,
            **extra,
        )

    @property
    def global_groups(self) -> Sequence[click.MultiCommand]:
        """Property which loads all global command groups from plugins and
        combines them with the built-in ones (eventually overriding the
        built-in ones if they are redefined by plugins).
        """
        return [cli, create_cli, *load_entry_points("global")]


def main():  # pragma: no cover
    """Main entry point. Look for a ``cli.py``, and, if found, add its
    commands to `GreenDeploy`'s before invoking the CLI.
    """
    cli_collection = GreenDeployCLI(project_path=Path.cwd())
    cli_collection()
