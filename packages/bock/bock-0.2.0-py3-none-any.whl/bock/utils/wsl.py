from pathlib import Path
from platform import uname
import shutil
import os
import subprocess
from typing import Tuple

class WSL:
  """
  Helper class to check functionality of WSL 

  """

  def __init__(self) -> None:
      pass

  @staticmethod
  def in_wsl() -> bool:
    """
    Checks if the script is executed out of WSL context or not. 

    WSL is thought to be the only common Linux kernel with Microsoft in the name, per Microsoft:
    https://github.com/microsoft/WSL/issues/4071#issuecomment-496715404
    """

    return 'microsoft' in uname().release

  @staticmethod
  def win_wsl_available() -> bool:
    """
    heuristic to detect if Windows Subsystem for Linux is available.
    Only meaningful from inside windows.

    Uses presence of /etc/os-release in the WSL image to say Linux is there.
    This is a de facto file standard across Linux distros.
    """
    if os.name == "nt":
        wsl = shutil.which("wsl")
        if not wsl:
            return False
        # can't read this file or test with
        # pathlib.Path('//wsl$/Ubuntu/etc/os-release').
        # A Python limitation?
        ret = subprocess.run(["wsl", "test", "-f", "/etc/os-release"])
        return ret.returncode == 0

    return False

  @staticmethod
  def get_wslwinhome() -> Path:
    """
    Returns the current user's wsl mounted home directory as Path. 
    Only works on Ubuntu 20.x or higher. 
    Might be somewhat performance intense

    Command used:
    wslpath "$(wslvar USERPROFILE)"
    see: https://superuser.com/questions/1271205/how-to-get-the-host-user-home-directory-in-wsl-bash
    https://stackoverflow.com/questions/4760215/running-shell-command-and-capturing-the-output

    """
    if not WSL.in_wsl():
      EnvironmentError("Trying to get mounted windows-home without active wsl environment.")

    cmd = 'wslpath "$(wslvar USERPROFILE)"'
    win_mnt_home = subprocess.check_output(cmd, shell=True, text=True).strip().replace(" ", "")
    return Path(win_mnt_home)

  @staticmethod
  def analyze_wsl_home_path(wsl_win_home: Path) -> str:
    """
    Takes in Path representation of the mounted windows home path and extracts the windows username.
    :param wsl_win_home Path representation of the mounted windows home

    """
    as_string = str(wsl_win_home)
    split = as_string.split(os.sep)
    return split[len(split)-1]

  @staticmethod
  def check_for_ubuntu20_lts() -> bool:
    """
    Checks if Ubuntu 20.x LTS is being used in the executing environment.
    Will return false if a different version or distro is being used.
    :returns boolean If Ubuntu 20.x.x LTS is being used.
    """
    cmd = 'cat /etc/lsb-release'
    ret = subprocess.check_output(cmd, shell=True, text=True).strip().lower()
    return ('ubuntu 20.' in ret) and ('lts' in ret) 

    