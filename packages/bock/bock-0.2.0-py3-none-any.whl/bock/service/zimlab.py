
import glob
from pathlib import Path
import os
import shutil
import tempfile
from shutil import copytree, ignore_patterns

class ZIMLab:
  """
  Service-class handling interaction with ZIMlab
  """
  # static variables
  PROJECTS_ROOT_URL = "https://zimlab.uni-graz.at/gams/projects"
  PROJECT_TEMPLATES_WWW_URL = "https://zimlab.uni-graz.at/gams/projects/templates/gams-www"

  def __init__(self, gams_local: Path) -> None:
    self.gams_local = gams_local

  @staticmethod
  def clone_project_www(project_abbr: str, clone_loc: str):
    """
    Takes in the convention-enforced project-abbr and clones from zimlab accordingly into requested folder.
    Clones into a folder with the name of given project-abbr.
    :param project_abbr Abbrevation of the GAMS project done at ZIM Graz.
    :param clone_loc dir to which the project gams-www should be checked out. 
    """

    if not Path.is_dir(Path(clone_loc)): raise NotADirectoryError(f"Given Path is not a directory. Given path: {clone_loc}") 

    # check if already checked out
    check_projabbr_path = clone_loc + os.sep + project_abbr
    if Path.is_dir(Path(check_projabbr_path)): raise IsADirectoryError(f"Project seems to be already available at: {check_projabbr_path}")

    # Awaited path on zimlab - enforced by convention
    repo_url  = f"{ZIMLab.PROJECTS_ROOT_URL}/{project_abbr}/gams-www" 
    # save to restore
    cur_cwd = os.curdir

    # clone into location in folder like project_abbr
    os.chdir(clone_loc)
    cmd = f"git clone {repo_url} {project_abbr}"
    os.system(cmd)

    # restore cwd
    os.chdir(cur_cwd)

  @staticmethod
  def copy_templates_www(project_abbr, clone_loc):
    """
    Clones gams-project templates to temp dir. Then copies files to the project folder in your gams-data/apache.
    Throws AssertionError if .xsl files are already found in target directory.
    :param project_abbr abbreviation of the gams project used on zim. (zimlab + locla folder) Enforced by convention on ZIM
    :param clone_loc location to where the files should be cloned to.
    """
    # destination path of copying
    toDirectory = clone_loc + os.sep + project_abbr
    if ZIMLab.check_for_xslfiles(toDirectory): raise AssertionError(f"There are already .xsl files available at: {toDirectory}. If you still want to setup the template files make sure to clean up given directory.")

    # create a temporary directory using the context manager
    with tempfile.TemporaryDirectory() as tmpdirpath:

      ZIMLab.clone_project_www("templates", tmpdirpath)

      # copy from tmp to apache/PROJECT_ABBR
      fromDirectory = tmpdirpath + os.sep + "templates"

      # change files in tmp location
      ZIMLab._adapt_template_files(fromDirectory, project_abbr)

      # fetch all files + copy
      for file_name in os.listdir(fromDirectory):

          # skip hidden files and readme.
          if file_name.startswith("."):
            continue
          elif "readme" in file_name.lower():
            continue

          source = fromDirectory + os.sep + file_name
          # rename files
          destination = toDirectory + os.sep + file_name

          if os.path.isfile(source):
            # Move to own method!
            # adapts temp files to specific project setup
            # ZIMLab._adapt_temp_template_files(file_name, source, project_abbr)
            shutil.copy(source, destination)
            print('Created file: ', destination)

          else:
            copytree(source, destination)
            print("Created dir: ", destination)

  
  @staticmethod
  def check_for_xslfiles(dir_path: str):
    """
    Checks if xsl files are inside given directory. Returns true if available false otherwise.
    :param dir_path path to be checked.
    """
    # throw error if project-files are available? or return boolean
    file_list = os.listdir(dir_path)

    for file in file_list:
      if ".xsl" in file:
        return True
    
    return False

  @staticmethod
  def _adapt_template_files(loc_folder: str, project_abbr: str):
    """
    Changes xslt / css / js gams project template files according to project abbreviation. Like renaming file
    (from project-static.xsl to MYABBR-static.xsl) and changing xsl file contents.
    :param loc_folder parent folder path of template files.
    :project_abbr convention based project abbreviation of the gams proect
    """
    # open files and adapt to project setup?

    for filename in glob.iglob(loc_folder + '**/**', recursive=True):
      if "static.xsl" in filename:
        text = open(filename, 'r').read().replace('<xsl:variable name="projectAbbr">templates</xsl:variable>', f'<xsl:variable name="projectAbbr">{project_abbr}</xsl:variable>')
        open(filename, 'w').write(text)
        os.rename(filename, filename.replace("project-", f"{project_abbr}-"))

      if ("object.xsl" in filename) or ("context.xsl" in filename) or ("search.xsl" in filename):
        text = open(filename, 'r').read().replace('<xsl:include href="templates-static.xsl"/>', f'<xsl:include href="{project_abbr}-static.xsl"/>')
        open(filename, 'w').write(text)
        os.rename(filename, filename.replace("templates-", f"{project_abbr}-"))

      if "templates.css" in filename:
        os.rename(filename, filename.replace("templates.css", f"{project_abbr}.css"))