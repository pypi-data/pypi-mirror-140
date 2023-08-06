
import subprocess
import click
import os

from bock.utils.wsl import WSL
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
    """Reset local gams data (available via Cirilo). """

    click.echo("*Trying to stop (if) running gams-local...\n")
    gams_local_path = str(GamsLocalFileService().gamslocal_path)
    old_cwd = os.curdir

    os.chdir(gams_local_path + os.sep + "gams-docker")
    # make sure gams not running
    subprocess.run(["docker-compose", "down"])
    # remove volumes
    subprocess.run(["docker", "volume", "prune"])
    os.chdir(old_cwd)
    click.echo("*Local GAMS data succesfully removed. Start local gams to check for deletion via Cirilo6.\n")

# 
#
#