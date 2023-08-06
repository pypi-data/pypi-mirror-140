

import os
from pathlib import Path
import tempfile
import subprocess
from shutil import copytree
from typing import Tuple

class GamsLocalDocker:
  """
  Encapsulates all methods related to the local docker environment of the local GAMS.
  Like access to docker logging etc.

  """

  DOCKER_CONTAINER = ["activemq", "blazegraph", "cocoon", "fcrepo4", "latex", "nexuscube", "proai", "relight", "skosifier", "toolbox", "triplestore",
                      "apache", "cm4f", "fcgate", "fits", "loris", "postgres", "rdf4j", "rscript", "solr", "treetagger", "verovio"]

  def __init__(self) -> None:
      pass


  @staticmethod
  def grab_logging(location: str) -> str:
    """
    Copies all available gams-local logs to specified location into gams-logs folder.
    :param location target to where logs should be copied. 
    :return path to the logs.
    """

    gams_logspath = location + os.sep + "gams-logs"
    if not os.path.isdir(gams_logspath):
      os.mkdir(gams_logspath)

    with tempfile.TemporaryDirectory() as tmpdirpath:
      
      logs_temp = tmpdirpath + os.sep + "logs"
      os.mkdir(logs_temp)  

      for container in GamsLocalDocker.DOCKER_CONTAINER:
        cmd = f"docker logs {container}"
        try:
          ret = subprocess.check_output(cmd, shell=True, text=True).strip().replace("  ", " ")
        except subprocess.CalledProcessError as err:
          print(str(err.stderr))
          raise SystemError(f"Awaited gams-local container '{container}' not found. Make sure that gams-local is active and running.")

        f = open( logs_temp + os.sep + f"{container}.log", "a")
        f.write(ret)
        f.close()

      # copy file out of tmp
      copytree(logs_temp, gams_logspath, dirs_exist_ok=True)
    
    return gams_logspath

  @staticmethod
  def start_gams(gams_local_path: Path) -> str:
    """
    Start local gams. Needs to have an adequate docker-compose.yaml in it's current working directory.
    :param gams_local_path Path representation of gams-docker on the current machine.
    :returns string of "gams-docker" (docker-compose.yaml lives) path on current machine
    """
    gams_localpath_str = str(gams_local_path)
    gams_dockerpath = gams_localpath_str + os.sep + "gams-docker"

    old_cwd = os.curdir
    os.chdir(gams_dockerpath)
    subprocess.run(["docker-compose", "up", "-d"])
    os.chdir(old_cwd)

    return gams_dockerpath

  def stop_gams(gams_local_path: Path) -> str:
    """
    Stop local gams. Needs to have an adequate docker-compose.yaml in it's current working directory.
    :param gams_local_path Path representation of gams-docker on the current machine.
    :returns string of "gams-docker" (docker-compose.yaml lives) path on current machine
    """

    gams_localpath_str = str(gams_local_path)
    gams_dockerpath = gams_localpath_str + os.sep + "gams-docker"
    old_cwd = os.curdir

    os.chdir(gams_dockerpath)
    # docker-compose down
    subprocess.run(["docker-compose", "down"])

    os.chdir(old_cwd)

  @staticmethod
  def check_gams_status() -> Tuple[bool, str]:
    """
    Prints out all running docker container status via docker command. 
    :returns Boolean if GAMS running AND outable report about current local gams.
    """

    report = ""
    is_running: bool = False
    cmd = 'docker container ls'
    docker_ps_return = subprocess.check_output(cmd, shell=True, text=True).strip().lower()
    
    if docker_ps_return.count("\n") == 0:
      report = "******\nLocal GAMS seems to be stopped.\n******" 
      is_running = False
    else:
      report = "******\nLocal GAMS seems to be running.\n******"
      is_running = True

    report += "\nOriginal report: \n"
    report += docker_ps_return 

    return (is_running, report)

  @staticmethod
  def update_gams(gams_local_path: Path):
    """
    Updates gams-docker files via running git pull in the gams-docker directory / local clone.
    :param gams_local_path Path to the user's gams-local
    """
    gams_localpath_str = str(gams_local_path)
    gams_dockerpath = gams_localpath_str + os.sep + "gams-docker"

    old_cwd = os.curdir
    os.chdir(gams_dockerpath)
    subprocess.run(["git", "pull"])
    os.chdir(old_cwd)

    return gams_dockerpath