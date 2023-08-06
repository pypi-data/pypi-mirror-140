
import click
import platform
from bock.utils.wsl import WSL

# Base Setup
#
# class definition is needed for external data and basic setup here
class Context:
    def __init__(self):
        # self.note = svc_note.Note()
        pass

# assign defined context to command initialization.
@click.group()
@click.pass_context
def cli(ctx):
    """Commands for getting info about your system (wsl etc.)."""
    ctx.obj = Context()
    pass

# 
#
#

# first real command in subcommand
@cli.command()
@click.pass_context
def system(ctx):
  """
  Provides basic info about the executing context of bock. 
  """
  click.echo(f"Running system: {platform.system()}")
  click.echo(f"OS-release: {platform.release()}")
  click.echo(f"Uname: {platform.uname()}")
  click.echo(f"Machine type: {platform.machine()}")
  click.echo(f"Network-node: {platform.node()}")
  click.echo(f"Using python version: {platform.python_version()}")
  click.echo(f"Ubuntu LTS 20.x being used as current distro in wsl: {'YES' if WSL.check_for_ubuntu20_lts() else '!NO! (Bock will only run under Ubuntu 20.x LTS)'}")