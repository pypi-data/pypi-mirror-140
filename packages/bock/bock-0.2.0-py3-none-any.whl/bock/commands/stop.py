
import click
from bock.service.GamsLocalDocker import GamsLocalDocker

from bock.service.GamsLocalFileService import GamsLocalFileService

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
    """Stop local gams as docker environment."""

    click.echo("*Stopping gams-local now...")

    GamsLocalDocker.stop_gams(
        GamsLocalFileService().gamslocal_path
    )

    click.echo("*gams-local stopping procedure end.")
# 
#
#