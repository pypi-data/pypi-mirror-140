
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
    """Get status report of local gams. """
    click.echo("!Getting status report...")
    _ , report = GamsLocalDocker.check_gams_status()
    click.echo(report)
    click.echo("!Status report end.")
    
