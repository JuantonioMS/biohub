import json
import jsonschema
import os
import subprocess

from biohub.utils import evalSentence

from biohub.conf.core.constants.path import PATH_CONF_CORE_SCHEMAS_APPS, \
                                            PATH_CONDA_ENVS, \
                                            PATH_SINGULARITY_IMAGES, \
                                            PATH_SYSTEM_FOLDERS


class Build:


#  MAIN_________________________________________________________________________________________________________________


    def _checkProcess(self) -> bool:

        if self._checkProcessConfiguration():

            self.logger.info("BUILD :: Checking process build")
            if not self._checkProcessBuild():

                self.logger.info(f"BUILD :: Installing process dependencies of {self.environment}")
                self._buildProcess()

                status = self._checkProcessBuild()
                if status: self.logger.info("BUILD :: Process build OK")
                else:      self.logger.error("BUILD :: Process build ERROR")

                return status

            else:
                self.logger.info("BUILD :: Process build OK")
                return True

        else: return False


#  BIOHUB BUILD_________________________________________________________________________________________________________


    def _checkBiohub(self) -> bool:

        if not self._checkBuildBiohub():
            self._buildBiohub()

        return self._checkBuildBiohub()


    def _checkBuildBiohub(self) -> bool:

        checks = []

        self.logger.info("BUILD :: Check mamba installation")
        checks.append(self._checkMambaInstallation())

        self.logger.info("BUILD :: Check singularity installation")
        checks.append(self._checkSingularityInstallation())

        self.logger.info("BUILD :: Check conda envs folder")
        checks.append(self._checkCondaFolder())

        self.logger.info("BUILD :: Check singularity images folder")
        checks.append(self._checkSingularityFolder())

        self.logger.info("BUILD :: Check system folder")
        checks.append(self._checkSystemFolder())

        return not any([not check for check in checks])



    def _checkMambaInstallation(self) -> bool: return not bool(subprocess.run("which mamba", executable = "/bin/bash", shell = True, capture_output = True).returncode)
    def _checkSingularityInstallation(self) -> bool: return not bool(subprocess.run("which singularity", executable = "/bin/bash", shell = True, capture_output = True).returncode)
    def _checkCondaFolder(self) -> bool: return PATH_CONDA_ENVS.exists()
    def _checkSingularityFolder(self) -> bool: return PATH_SINGULARITY_IMAGES.exists()
    def _checkSystemFolder(self) -> bool: return PATH_SYSTEM_FOLDERS.exists()



    def _buildBiohub(self) -> None:

        self.runCommand(f"mkdir --parents {PATH_CONDA_ENVS}")
        self.runCommand(f"mkdir --parents {PATH_SINGULARITY_IMAGES}")
        self.runCommand(f"mkdir --parents {PATH_SYSTEM_FOLDERS}")


#  JSON CONFIGURATION___________________________________________________________________________________________________


    def _checkProcessConfiguration(self) -> bool:

        self.logger.info(f"BUILD :: Checking {self.jsonFile} content")

        try:
            jsonschema.validate(self.jsonInfo,
                                json.load(open(PATH_CONF_CORE_SCHEMAS_APPS, "r")))

            self.logger.info(f"BUILD :: {self.jsonFile} content OK")
            return True

        except Exception as error:
            self.logger.error(f"BUILD :: {self.jsonFile} is not properly configured\n{error}")
            return False


#  BUILD________________________________________________________________________________________________________________


    def _checkProcessBuild(self) -> bool:

        if self.type == "system":        status = self._checkProcessBuildSystem()
        elif self.type == "conda":       status = self._checkProcessBuildConda()
        elif self.type == "singularity": status = self._checkProcessBuildSingularity()

        return status


    #  TODO
    def _checkProcessBuildSystem(self) -> bool:      return any([env in str(self.environment) for env in os.listdir(PATH_SYSTEM_FOLDERS)])
    def _checkProcessBuildConda(self) -> bool:       return any([env in str(self.environment) for env in os.listdir(PATH_CONDA_ENVS)])
    def _checkProcessBuildSingularity(self) -> bool: return any([img in str(self.environment) for img in os.listdir(PATH_SINGULARITY_IMAGES)])



    def _buildProcess(self) -> None:

        for command in self.jsonInfo["build"]:
            self.runCommand(evalSentence(command, self = self))