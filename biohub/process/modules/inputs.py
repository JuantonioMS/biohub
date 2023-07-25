import copy
from pathlib import Path
from typing import Union

from biohub.storage import File, Folder
from biohub.process.wrapper import Input
from biohub.utils import verifyPath, getDefaultRole

from biohub.conf.core.constants.process import PROCESS_DEFAULT_ROUTE


class Inputs:


    @property
    def defaultInputs(self) -> dict:

        """Get default options for common route and specfic route from conf/apps/<tool>.yaml"""

        auxDefaultInputs = {}

        try: allInputs = self.jsonInfo["inputs"]
        except KeyError: allInputs = []

        for route in (PROCESS_DEFAULT_ROUTE, self.route):
            for element in allInputs:

                if element["route"] == route:
                    auxDefaultInputs[element["role"]] = Input(**element)

        return auxDefaultInputs



    def _setInputs(self, **inputs) -> dict:

        #  Merge user inputs with default inputs

        self.logger.info(f"INPUTS :: Wrap User Inputs :: Wrapping {len(inputs)} user inputs")
        inputs = self._wrapUserInputs(**inputs)

        self.logger.info(f"INPUTS :: Merge Inputs :: Merging user and default inputs")
        inputs = self._mergeInputs(**inputs)

        self.logger.info(f"INPUTS :: Solve inputs :: Solving unresolved inputs")
        inputs = self._solveInputs(**inputs)

        if any(input is None for input in inputs.values()):
            inputs = {}

        return inputs



    def _wrapUserInputs(self, **inputs) -> dict:

        auxInputs = {}
        for role, input in inputs.items():

            if isinstance(input, (Path, str)):
                auxInputs[role] = Input(role = role,
                                        biohubFile = verifyPath(input))


            elif isinstance(input, (File, Folder)):
                auxInputs[role] = Input(role = role,
                                        biohubFile = input,
                                        pathPrefix = self.entity.path)


            elif isinstance(input, Input):
                auxInputs[role] = input


            else:
                self.logger.warning(f"INPUTS :: Wrap User Inputs :: Input {role} type is not valid (type: {type(input)})")

        return auxInputs



    def _mergeInputs(self, **inputs) -> dict:

        auxInputs = {}
        for role, defaultInput in self.defaultInputs.items():

            if role in inputs: #  El usuario ha definido el input

                #  Si existe un prefijo para el input y el usuario no lo ha definido previamente (via Wrapper)
                if defaultInput.name and not inputs[role].name:
                    inputs[role]._name = defaultInput.name

                auxInputs[role] = inputs[role] #  Cargamos el input

            #  Si no ha definido el input
            else:
                auxInputs[role] = defaultInput

        return auxInputs



    def _solveInputs(self, **inputs) -> dict:

        auxInputs = {}
        for role, input in inputs.items():

            #  Si el input necesita resolver sentencias evaluables, lo dejamos para después
            if input.evalPending: auxInputs[role] = input

            else:
                #  Si ya tiene un fichero asignado lo añadimos
                if hasattr(input, "_biohubFile"): auxInputs[role] = input

                #  Sino, creamos el input intentando encontrar el fichero indicado
                else:
                    auxInputs[role] = self._createInput(input)

        return auxInputs



    def _createInput(self, input: Input) -> Union[Input, None]:

        file = self._selectInput(input)

        if file:
            input.biohubFile = file
            input.pathPrefix = self.entity.path

        else: input = None

        return input



    def _selectInput(self, input: Input) -> Union[File, None]:

        field = {"required" : {},
                 "optimal"  : {}}

        for element in input.selection:
            for priority in ("required", "optimal"):

                try:

                    value = element[priority]

                    if isinstance(value, list): field[priority][element["target"]] = set(value)
                    else: field[priority][element["target"]] = value

                except KeyError: pass


        required, optimal = field["required"], field["optimal"]

        optimalFieldView = []
        for key, value in optimal.items():

            if isinstance(value, (list, tuple, set)): [optimalFieldView.append((key, element)) for element in value]
            else: optimalFieldView.append((key, value))

        while True:

            candidates = self.entity.selectFile(**self._joinFieldViews(required, optimalFieldView))

            if candidates:

                self.logger.info(f"INPUTS :: {input.role} candidate file found")

                if len(candidates) > 1:
                    self.entity.logger.warning(f"INPUTS :: {input.role} non unique candidate")

                return candidates[0]

            else:

                if not optimalFieldView: break

                optimalFieldView = optimalFieldView[:-1]

            if len(optimalFieldView) == 0:

                #self.logger.warning(f"Process {self.id} :: INPUTS :: No candidate files for role {info.role}")

                break

        return None



    @staticmethod
    def _joinFieldViews(required: dict, optimalFieldView: list) -> dict:

        fieldView = copy.deepcopy(required)

        for target, value in optimalFieldView:

            if target in fieldView and isinstance(fieldView[target], set): fieldView[target].add(value)
            else: fieldView[target] = value

        return fieldView