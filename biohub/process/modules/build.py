class Build:


    def _checkAppBuild(self):

        if self.type == "anaconda":
            self._checkAppBuildAnaconda()


    def _checkAppBuildAnaconda(self):

        _, result = self.runCommand("/home/virtualvikings/conda/bin/conda env list", captureOutput = True)

        if not any([self.environment in i for i in result.split("\n")]):
            self.runCommand(*self.jsonInfo["build"])