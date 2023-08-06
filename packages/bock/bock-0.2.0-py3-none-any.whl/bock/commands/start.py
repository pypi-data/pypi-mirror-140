
import click

from bock.utils.wsl import WSL
from bock.service.GamsLocalFileService import GamsLocalFileService
from bock.service.GamsLocalDocker import GamsLocalDocker


# Base Setup
#
# class definition is needed for external data and basic setup here
class Context:
    def __init__(self):
        # self.note = svc_note.Note()
        pass

# will launch command directly


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    """Start local gams as docker environment."""

    click.echo("*Starting gams-local now...")

    GamsLocalDocker.start_gams(
        GamsLocalFileService().gamslocal_path
    )

    click.echo("*gams-local end of starting precedure.")
    
