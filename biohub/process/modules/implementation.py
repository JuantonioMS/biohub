from biohub.utils import evalSentence

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
    def sentences(self) -> dict:

        aux = {}

        try:
            aux = self.jsonInfo["implementation"]["sentences"]
        except KeyError: pass

        return aux


    @property
    def sentencesBody(self) -> list:

        aux = []

        if "body" in self.sentences:

            for route in (self.route, "common"):
                for element in self.sentences["body"]:

                    if not aux:

                        try:
                            if element["route"] == route:
                                aux = element["sentences"]
                        except KeyError: continue

        if not aux: aux = [DEFAULT_PROCESS_SENTENCE]

        return aux


    @property
    def sentencesHead(self) -> list:

        aux = []

        if "head" in self.sentences:

            for route in (self.route, "common"):
                for element in self.sentences["head"]:

                    if not aux:

                        try:
                            if element["route"] == route:
                                aux = element["sentences"]
                        except KeyError: continue

        return aux


    @property
    def sentencesTail(self) -> list:

        aux = []

        if "tail" in self.sentences:

            for route in (self.route, "common"):
                for element in self.sentences["tail"]:

                    if not aux:

                        try:
                            if element["route"] == route:
                                aux = element["sentences"]
                        except KeyError: continue

        return aux



    def _runSentences(self, sentences: list, **kwargs) -> None:

        if isinstance(sentences, str):  sentences = [sentences]

        for sentence in sentences:

            sentence = evalSentence(sentence, self = self, **kwargs)

            self.runCommand(sentence)



    def _runProcess(self,
                    inputs: dict = {},
                    outputs: dict = {},
                    options: dict = {}) -> None:

        self.logger.info(f"Process {self.id} :: IMPLEMENTATION :: Creating temporal directory {self.temporalDirectory}")
        self._createTemporalDirectory()

        self.logger.info(f"Process {self.id} :: IMPLEMENTATION :: Running core process")
        self._coreProcess(inputs = inputs,
                          outputs = outputs,
                          options = options)



    def _createTemporalDirectory(self) -> None:

        self.runCommand(f"mkdir {self.temporalDirectory}")



    def _coreProcess(self,
                     inputs: dict = {},
                     outputs: dict = {},
                     options: dict = {}) -> None:

        for sentence in self.sentencesBody:

            sentence = sentence.replace("<command>", self.command)\
                               .replace("<inputs>", self._CLI_SEPARATOR_INPUTS.join([str(element) for element in inputs.values()]))\
                               .replace("<outputs>", self._CLI_SEPARATOR_OUTPUTS.join([str(element) for element in outputs.values()]))\
                               .replace("<options>", self._CLI_SEPARATOR_OPTIONS.join([str(element) for element in options.values()]))

            sentence = evalSentence(sentence,
                                    self = self,
                                    inputs = inputs,
                                    outputs = outputs,
                                    options = options)

            if self.type == "system": self.runSystemPackage(sentence)

            elif self.type == "anaconda": self.runCondaPackage(sentence)

            elif self.type == "singularity": self.runSingularityPackage(sentence)

            else: self.logger.warning(f"Process {self.id} :: IMPLEMENTATION :: {self.type} is not a valid process type")