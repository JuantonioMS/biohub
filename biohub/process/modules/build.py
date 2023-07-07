import os

from biohub.utils import evalSentence

from biohub.conf.general.constant import SINGULARITY_IMAGES_PATH

class Build:


    def _checkAppBuild(self) -> None:

        if self.type == "anaconda":
            self._checkAppBuildAnaconda()

        if self.type == "singularity":
            self._checkAppBuildSingularity()


    def _checkAppBuildAnaconda(self) -> None:

        _, result = self.runCommand("conda env list", verbosity = False)

        if not any([self.environment.split("/")[-1] in i for i in result.split("\n")]):

            self.logger.info(f"BUILD :: Installing conda env {self.environment}")

            for command in self.jsonInfo["build"]:


                while "eval##" in command:
                    command = evalSentence(command, self = self)

                self.runCommand(command)



    def _checkAppBuildSingularity(self) -> None:

        if not any([self.environment.split("/")[-1] in i for i in os.listdir(SINGULARITY_IMAGES_PATH)]):

            self.logger.info(f"BUILD :: Installing singularity image {self.environment}")

            for command in self.jsonInfo["build"]:

                while "eval##" in command:
                    command = evalSentence(command, self = self)

                self.runCommand(command)