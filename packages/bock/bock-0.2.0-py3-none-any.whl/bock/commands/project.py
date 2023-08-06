
import click
from bock.service.GamsLocalFileService import GamsLocalFileService
from bock.service.zimlab import ZIMLab

# Base Setup
#
# class definition is needed for external data and basic setup here
class Context:
    def __init__(self):
        self.gfile_service = GamsLocalFileService()

# assign defined context to command initialization.
@click.group()
@click.pass_context
def cli(ctx):
    """Commands related to gams-projects. """
    ctx.obj = Context()
    pass

# 
#
#

# first real command in subcommand
@cli.command()
@click.pass_context
@click.argument('project_abbr')
def setup(ctx, project_abbr):
  """ 
    Setup a gams4+ project for your local gams.\n
    :param project_abbr ZIM/GAMS project abbreviation as used in zimlab and auth.
  """
  click.echo(f"Initializing project for: {project_abbr}")
  click.echo(f"Found gams-local root at: {str(ctx.obj.gfile_service.gamslocal_path)}")
  click.echo(f"Found apache dir at: {str(ctx.obj.gfile_service.gamslocal_apache)}")

  # cloning project from zimlab 
  GamsLocalFileService.assert_project_abbr(project_abbr)
  ZIMLab.clone_project_www(project_abbr=project_abbr, clone_loc=str(ctx.obj.gfile_service.gamslocal_apache))
  click.echo(f"Succesfully cloned project {project_abbr} from zimlab to: {str(ctx.obj.gfile_service.gamslocal_apache)}")

  # copy over gams-templates files.
  if click.confirm("Do you want to copy over gams-project templates files to your project folder? (Will stop if there are already xslt-files inside your local clone)"):
    ZIMLab.copy_templates_www(project_abbr, str(ctx.obj.gfile_service.gamslocal_apache))

@cli.command()
@click.pass_context
def repair(ctx):
  """
  DANGEROUS! Removes all dos line-endings inside /apache files.
  Will convert all files inside the apache folder from dos to unix line-endings.
  Might mess with files in the apache folder.
  """
  if click.confirm('Transform dos line-endings maybe causing problems inside your /apache ?'):
    ctx.obj.gfile_service.dos2unix_apache_folder()
  