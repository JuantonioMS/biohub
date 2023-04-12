class Build:


    def _checkAppBuild(self):

        if self.type == "anaconda":
            self._checkAppBuildAnaconda()


    def _checkAppBuildAnaconda(self):

        _, result = self.runCommand("conda env list")

        if not any([self.environment in i for i in result.split("\n")]):
            self.entity.logger.info(f"Process {self.id} :: BUILD :: Installing conda env")
            self.runCommand(*self.jsonInfo["build"])