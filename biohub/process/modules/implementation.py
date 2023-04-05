from biohub.conf.general.constant import DEFAULT_PROCESS_SENTENCE

class Implementation:


    @property
    def command(self) -> str:

        aux = ""

        for route in (self.route, "common"):

            if not aux:

                try:
                    for element in self.jsonInfo["implementation"]["commands"]:

                        if element["route"] == route:
                            aux = element["command"]
                            break

                except KeyError: continue

        if not aux: aux = self.tool

        return aux


    @property
    def sentence(self) -> str:

        aux = ""

        for route in (self.route, "common"):

            if not aux:

                try:
                    for element in self.jsonInfo["implementation"]["sentences"]:

                        if element["route"] == route:
                            aux = element["sentence"]
                            break

                except KeyError: continue

        if not aux: aux = DEFAULT_PROCESS_SENTENCE

        return aux



    def _runProcess(self,
                    inputs: dict = {},
                    outputs: dict = {},
                    options: dict = {}) -> None:

        self.entity.logger.info(f"Process {self.id} :: IMPLEMENTATION :: Creating temporal directory {self.temporalDirectory}")
        self._createTemporalDirectory()

        self.entity.logger.info(f"Process {self.id} :: IMPLEMENTATION :: Running core process")
        self._coreProcess(inputs = inputs,
                          outputs = outputs,
                          options = options)



    def _createTemporalDirectory(self) -> None:

        self.runCommand(f"mkdir {self.temporalDirectory}")



    def _coreProcess(self,
                     inputs: dict = {},
                     outputs: dict = {},
                     options: dict = {}) -> None:

        sentence = self.sentence.replace("<command>", self.command)\
                                .replace("<inputs>", " ".join([str(element) for element in inputs.values()]))\
                                .replace("<outputs>", " ".join([str(element) for element in outputs.values()]))\
                                .replace("<options>", " ".join([str(element) for element in options.values()]))

        if self.type == "system": self.runSystemPackage(sentence)

        elif self.type == "anaconda": self.runCondaPackage(sentence)

        elif self.type == "singularity": self.runSingularityPackage(sentence)

        else: self.entity.logger.warning(f"Process {self.id} :: IMPLEMENTATION :: {self.type} is not a valid process type")