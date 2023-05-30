import copy
from pathlib import Path
from typing import Union

from biohub.storage import File
from biohub.process.wrapper import Input
from biohub.utils import verifyPath


class Inputs:


    @property
    def defaultInputs(self) -> dict:

        """Get default options for common route and specfic route from conf/apps/<tool>.yaml"""

        auxDefaultInputs = {}

        try: allInputs = self.jsonInfo["inputs"]
        except KeyError: allInputs = []

        for route in ("common", self.route):
            for element in allInputs:

                if element["route"] == route:

                    auxDefaultInputs[element["role"]] = Input(**element)

        return auxDefaultInputs



    def _setInputs(self, **inputs) -> dict:

        #  Merge user inputs with default inputs

        self.logger.info(f"Process {self.id} :: INPUTS :: Creating user inputs")
        inputs = self._createUserInputs(**inputs)

        self.logger.info(f"Process {self.id} :: INPUTS :: Merging user inputs and default inputs")
        inputs = self._mergeInputs(inputs, self.defaultInputs)

        self.logger.info(f"Process {self.id} :: INPUTS :: Creating BioHub File objects")
        inputs = self._createPendingInputs(**inputs)

        if any(input is None for input in inputs.values()):
            inputs = {}

        return inputs



    def _createUserInputs(self, **inputs):

        auxInputs = {}
        for role, input in inputs.items():

            self.logger.info(f"Process {self.id} :: INPUTS :: User input -> role: {role}; type: {type(input)}; input: {input}")

            if isinstance(input, Input):
                auxInputs[role] = input

            elif isinstance(input, File):
                auxInputs[role] = Input(role = role,
                                        biohubFile = input,
                                        pathPrefix = self.entity.path)

            elif isinstance(input, (Path, str)):
                auxInputs[role] = Input(role = role,
                                        biohubFile = verifyPath(input))

            else:
                self.logger.warning(f"Process {self.id} :: INPUTS :: Not valid input type!")

        return auxInputs


    # TODO revisar la no creación de cosas
    def _mergeInputs(self, inputs: dict, defaultInputs: dict) -> dict:

        auxInputs = {}
        for role, defaultInput in defaultInputs.items():

            if role in inputs: #  El usuario ha definido el input

                #  Si existe un prefijo para el input y el usuario no lo ha definido previamente (via Wrapper)
                if defaultInput.name and not inputs[role].name:

                    self.logger.info(f"Process {self.id} :: INPUTS :: Adding input name to user input -> role: {role}; name: {defaultInput.name}")

                    inputs[role]._name = defaultInput.name

                auxInputs[role] = inputs[role] #  Cargamos el input

            #  Si no ha definido el input
            else:

                self.logger.info(f"Process {self.id} :: INPUTS :: Completing with default input -> role: {role}")

                auxInputs[role] = defaultInput

        return auxInputs



    def _createPendingInputs(self, **inputs) -> dict:

        auxInputs = {}
        for role, input in inputs.items():

            if input.evalPending: auxInputs[role] = input
            else:
                if hasattr(input, "_biohubFile"):
                    auxInputs[role] = input

                else:
                    auxInputs[role] = self._createInput(input)

        return auxInputs



    def _createInput(self, input: Input) -> Union[Input, None]:

        file = self._selectInput(input.selection)

        if file: input.biohubFile = file
        else: input = None

        input.pathPrefix = self.entity.path

        return input



    def _selectInput(self, info: list) -> Union[File, None]:

        self.logger.info(f"Process {self.id} :: INPUTS :: Selecting input")

        field = {"required" : {},
                 "optimal"  : {}}

        for element in info:

            for priority in ("required", "optimal"):

                try:

                    value = element[priority]

                    if isinstance(value, list): field[priority][element["target"]] = set(value)
                    else: field[priority][element["target"]] = value

                except KeyError: pass


        required, optimal = field["required"], field["optimal"]

        optimalFieldView = [(field, value) for field in optimal for value in optimal[field]]

        while True:

            fieldView = copy.deepcopy(required)
            for field, value in optimalFieldView:

                if field in fieldView:
                    fieldView[field].add(value)

                else:
                    if field in ("outlines", "tags"): fieldView[field] = {value}
                    else: fieldView[field] = value

            candidates = self.entity.selectFile(**fieldView)

            if candidates:

                self.logger.info(f"Process {self.id} :: INPUTS :: Candidate files found: {len(candidates)}")
                if len(candidates) > 1: self.entity.logger.warning("No unique candidate file found")

                return candidates[0]

            else:
                optimalFieldView = optimalFieldView[:-1]

            if len(optimalFieldView) == 0:

                #self.logger.warning(f"Process {self.id} :: INPUTS :: No candidate files for role {info.role}")

                break

        return None
