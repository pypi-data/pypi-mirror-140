
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
    """Update local GAMS installation. At next start local GAMS will download additionally required files."""

    click.echo("bock: Updating gams-local now...")

    GamsLocalDocker.update_gams(
        GamsLocalFileService().gamslocal_path
    )

    click.echo("bock: Update process finished. (Additional files will be downloaded at next GAMS local start if necessary)")
    
