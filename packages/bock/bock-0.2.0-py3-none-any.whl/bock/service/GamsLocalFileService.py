
import os
from pathlib import Path
from bock.utils.wsl import WSL
import glob

class GamsLocalFileService:
    def __init__(self) -> None:
        # will thow NotImplementedError outside wsl.
        self.check_wsl_active()
        self.check_if_ubuntu20lts()
        self.win_home_path = WSL.get_wslwinhome()
        self.win_usr_name = WSL.analyze_wsl_home_path(self.win_home_path)
        self.default_gamslocal = "gams-local"
        # will throw an error if the expected folder is not available
        self.gamslocal_path = self._win_get_gamslocal_root()
        # apache dir (where projects / assets / etc. are)
        self.gamslocal_apache = self._getwsl_apache_gamslocal(
            self.gamslocal_path)

    def check_wsl_active(self) -> True:
        """
        Returns True if wsl is the executing context. Otherwise will throw a NotImplementedError
        """
        # check if wsl is the execution environment of the script
        if WSL.in_wsl():
            return True
        else:
            # check if wsl would be available
            if WSL.win_wsl_available():
                raise NotImplementedError(
                    "Running bock outside wsl is currently not supported but WSL seems to be installed. Type 'wsl' in your cmd and start bock from there!")
            else:
                raise NotImplementedError(
                    "Running bock outside wsl is currently not supported. WSL seems not to be installed")

    def win_verify_rootfolder(self, exp_gamslocal_path: Path) -> bool:
        """
        Method checks if the default wsl root-folder is correctly setup.
        :param exp_gamslocal_path Path of expected gams-local location on the system.

        """
        return Path.exists(exp_gamslocal_path) and Path.is_dir(exp_gamslocal_path)

    def check_if_ubuntu20lts(self):
        """
        Uses WSL class to verify that Ubuntu 20.x LTS is running otherwise raises a NotImplementedError.
        """
        if WSL.check_for_ubuntu20_lts():
            pass
        else:
            raise NotImplementedError(
                "Running bock outside ubuntu 20.x LTS is currently not supported. Please make sure to run Ubuntu 20.x as your distro.")

    def _win_get_gamslocal_root(self) -> Path:
        """
        Retrieves Path representation of gams-local folder.
        """

        win_home_str = str(self.win_home_path)
        exp_gamslocal_path = Path(
            win_home_str + os.sep + self.default_gamslocal)
        is_default = self.win_verify_rootfolder(
            exp_gamslocal_path=exp_gamslocal_path)
        if not is_default:
            raise NotADirectoryError(
                "gams-local dir not available at user home! Checked for path: ", str(exp_gamslocal_path))

        return exp_gamslocal_path

    def _getwsl_apache_gamslocal(self, gamslocal_path: Path):
        """
        Takes in the Path representation of the gams_local directory.
        Returns the expected location of the apache directory.
        """
        apache_path = Path(str(gamslocal_path) + os.sep +
                           "gams-data" + os.sep + "apache")
        if not Path.is_dir(apache_path):
            raise NotADirectoryError(
                "There appears to be no gams-data/apache in your gams-local directory. Please rerun the initial setup.sh. Got gams_local path: ", str(gamslocal_path))

        return Path(str(self.gamslocal_path) + os.sep + "gams-data" + os.sep + "apache")

    @staticmethod
    def assert_project_abbr(project_abbr: str) -> None:
        """
        Takes in the GAMS project abbrevation and throws an AssertionError when project_abbr has a forbidden value.
        Check the intern forbidden array for details.
        :param project_abbr project abbreviation as chosen on zimlab.
        """

        forbidden = ["3dhop",
                     "cirilo.properties",
                     "cm4f.org",
                     "config",
                     "css",
                     "doc",
                     "editionviewer",
                     "errors",
                     "icons",
                     "keycloak",
                     "lido",
                     "mei",
                     "mets",
                     "mirador",
                     "mirador-plugins",
                     "models",
                     "openapi",
                     "osd",
                     "osdviewer",
                     "platin",
                     "rtiviewer",
                     "schemes",
                     "storymap",
                     "tei",
                     "verovio",
                     "viewer",
                     "xsl",
                     "xsl-tokenizer"
                     ]

        if project_abbr in forbidden:
            raise AssertionError(f"Chosen project abbreviation is forbidden. Will cause conflicts when going to production. Forbidden values are: {str(forbidden)}")

    def dos2unix_apache_folder(self):
        """
        Method tries to convert all files inside the local apache folder. From \r\n to \n. 
        Will only work on files with "textual" data.  
        """
        for filename in glob.iglob(str(self.gamslocal_apache) + '**/**', recursive=True):
            if not Path.is_file(Path(filename)):
                continue

            try:
                text = open(filename, 'r').read().replace('\r\n', '\n')
                open(filename, 'w').write(text)
                print("**dos2unix on file**: ", filename)
            except UnicodeDecodeError as e:
                pass