from biohub.utils import evalSentence

class Build:


    def _checkAppBuild(self):

        if self.type == "anaconda":
            self._checkAppBuildAnaconda()


    def _checkAppBuildAnaconda(self):

        _, result = self.runCommand("conda env list", verbosity = False)

        if not any([self.environment.split("/")[-1] in i for i in result.split("\n")]):


            self.entity.logger.info(f"Process {self.id} :: BUILD :: Installing conda env {self.environment}")

            for command in self.jsonInfo["build"]:

                print("---->", command)

                while "eval##" in command:
                    sentence = "->" + command.split("->")[1].split("<-")[0] + "<-"
                    result = evalSentence(sentence[2:-2],
                                          self = self)
                    command = command.replace(sentence, str(result))
                    print(command)

                self.runCommand(command)