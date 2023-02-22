from xml.etree import ElementTree as ET
from pathlib import Path
import subprocess
from datetime import datetime, timedelta
import rich
from typing import Union, Any

from pattern.en import singularize

import json

import copy

from biohub.utils import BioHubClass
from biohub.utils import verifyPath, readYaml, evalSentence
from biohub.utils.wrapper import Input, Output, Option

from biohub.file import File


APPS_DIRECTORY = Path(Path(Path(__file__).parent, "../conf"), "apps")

DEFAULT_TYPE = "system"
DEFAULT_ENVIRONMENT = "base"
DEFAULT_ROUTE = "common"
DEFAULT_SENTENCE = "<command> <inputs> <options>"

DEFAULT_EXCLUDED_OPTIONS = ("threads", "outputDirectory")

class Process(BioHubClass):

    """Orientado de forma estándar a procesos Subject2Subject y Project2Project"""

    def __init__(self,
                 xmlElement: ET.Element = ET.Element("process"), #  Útil para importar
                 entity = None, #  Sujeto o proyecto
                 save: bool = True, #  Si el proceso se debe añadir o no  a la entidad
                 duplicate: bool = False, #  Si False, si se detecta un proceso completado igual, no se ejecutará
                 **attrs) -> None:

        self.entity = entity

        self.save = save
        self.duplicate = duplicate

        super().__init__(xmlElement, **attrs)

        if not hasattr(self, "simultaneousTasks"): self.simultaneousTasks = 1

        if not hasattr(self, "threads"): self.threads = 1
        if not hasattr(self, "threadsPerCore"): self.threadsPerCore = 2

        if not hasattr(self, "cores"): self.cores = 1 if self.threads < 3 else self.threads // self.threadsPerCore

        if not hasattr(self, "threadsPerTask"): self.threadsPerTask = self.threads
        if not hasattr(self, "coresPerTask"): self.coresPerTask = self.cores

        if not hasattr(self, "distributedMemory"): self.distributedMemory = False
        if not hasattr(self, "coresPerNode"): self.coresPerNode = 40



    def newId(self) -> str:
        return "bhPR" + super().newId()



    def minimumBuild(self) -> None:

        if self.framework is None:
            self.framework = self.__class__.__base__.__name__.lower()

        if self.tool is None:
            self.tool = self.__class__.__name__.lower()

        if self.type is None:

            try: self.type = self.jsonInfo["info"]["type"]
            except KeyError: self.type = DEFAULT_TYPE


        if self.environment is None:

            try: self.environment = self.jsonInfo["info"]["environment"]
            except KeyError: self.environment = DEFAULT_ENVIRONMENT

        if self.route is None:

            try: self.route = self.jsonInfo["implementation"]["defaultRoute"]
            except KeyError: self.route = DEFAULT_ROUTE

        super().minimumBuild()



    @property
    def jsonInfo(self) -> dict:

        try: return json.load(open(f"{APPS_DIRECTORY}/{self.framework}/{self.tool}.json"))
        except FileNotFoundError: return {}


    #%%  XML special tags_______________________________________________________________________________________________


    @property
    def _xmlElementTags(self) -> set: return {"framework", "tool", "route",
                                              "type", "environment"} | super()._xmlElementTags

    @property
    def _xmlSpecialTags(self) -> set:
        return {"duration", "inputs", "outputs", "options"} | super()._xmlSpecialTags


    #%%  Getters built-in methods_______________________________________________________________________________________

    def __getXmlSpecialTag__(self, attr: str) -> Any:

        if attr == "duration":

            try:

                duration = self._xmlElement.attrib[attr]

                hours, minutes, seconds = duration.split(":")
                seconds, microseconds = seconds.split(".")

                return timedelta(hours = int(hours),
                                 minutes = int(minutes),
                                 seconds = int(seconds),
                                 microseconds = int(microseconds))

            except KeyError: return None


        elif attr in {"inputs", "outputs"}:

            aux = {}

            element = self._xmlElement.find(attr)

            if element is not None:
                for subelement in element:

                    #  It is a Path
                    if "/" in subelement.text:
                        aux[subelement.attrib["role"]] = Input(biohubFile = Path(subelement.text),
                                                               role = subelement.attrib["role"])

                    #  Is is an ID
                    else:

                        if attr == "inputs":
                            wrapper = Input(biohubFile = self.entity.files[subelement.text],
                                            role = subelement.attrib["role"])
                        else:

                            wrapper = Output(biohubFile = self.entity.files[subelement.text],
                                             role = subelement.attrib["role"])

                        aux[subelement.attrib["role"]] = wrapper

            return aux


        elif attr == "options":

            aux = {}

            element = self._xmlElement.find(attr)

            if element is not None:

                for subelement in element:

                    role = subelement.attrib["role"]

                    for char in (" ", ":", "="):

                        if char in subelement.text:

                            name, value = subelement.text.split(char)
                            format = f"<name>{char}<value>"

                            aux[role] = Option(name = name,
                                               value = value,
                                               format = format,
                                               role = role)

                            break

                    else:
                        name, value = subelement.text, True

                        aux[role] = Option(name = name,
                                           value = value,
                                           role = role)

            return aux

        else: return super().__getXmlSpecialTag__(attr)


    #%%  Setters built-in methods_______________________________________________________________________________________


    def __setXmlSpecialTag__(self, attr: str, value: Any) -> None:


        if attr == "duration":

            if isinstance(value, timedelta):

                hours = int(value.total_seconds()//3600)
                minutes = f"{int(value.total_seconds()/60%60):0>2}"
                seconds = f"{int(value.total_seconds()%60):0>2}"
                microseconds = f"{value.microseconds:0>6}"

                self._xmlElement.attrib[attr] = f"{hours}:{minutes}:{seconds}.{microseconds}"

        elif attr in {"inputs", "outputs", "options"}:

            container = ET.SubElement(self._xmlElement, attr)

            for subValue in value.values():

                subelement = ET.SubElement(container, singularize(attr))
                subelement.attrib["role"] = subValue.role

                if attr != "options": subelement.text = subValue.id
                else: subelement.text = str(subValue)

        else: return super().__setXmlSpecialTag__(attr, value)


    #%%  _______________________________________________________________________________________________________________


    #  _________________________CLI Run Methods_________________________


    def runCommand(self, *args, captureOutput: bool = False, verbosity: bool = True) -> None:

        """
        Ejecuta comandos del sistema. Retorna el valor de ejecución resultante. Suele ser 0 el valor de todo correcto.
        Tiene la opción de capturar la salida si captureOuput es True y retorna el output.
        """

        if verbosity: Process.commandPrint(*args)
        output = subprocess.run(" ".join(args),
                                shell = True,
                                executable = "/bin/bash",
                                capture_output = captureOutput)

        if captureOutput:
            return output.returncode, output.stdout.decode("UTF8")

        else:
            return output.returncode



    def runCondaPackage(self, *args, env: str = None, captureOutput: bool = False) -> None:

        """
        Ejecuta comandos recogidos en entornos conda de forma similar al método runCommand
        """

        #  Búsqueda del shell de conda instalado en el sistema
        condaShell = "/".join(subprocess.getoutput("which conda").split("/")[:-2])

        if not env:
            env = self.environment

        #  Ruta completa a la shell de conda
        condaShell = f"{condaShell}/etc/profile.d/conda.sh"

        # Montando la llamada al paquete junto a la inicializacion de la shell y el entorno
        commandLine = " && ".join([f"{condaShell}"] + [f"conda activate {env}"] + [" ".join(args)])

        Process.commandPrint(commandLine)
        output = subprocess.run(f". {commandLine}",
                                shell = True,
                                executable = "/bin/bash",
                                capture_output = captureOutput)

        if captureOutput:
            return output.returncode, output.stdout.encode("UTF8")

        else:
            return output.returncode


    #  TODO
    def runSingularityPackage(self, *args):
        return ""

    #  TODO
    def runSystemPackage(self, *args):
        return ""


    #%% Prints__________________________________________________________________________________________________________

    @staticmethod
    def richPrint(*msgs, color = "bright_red") -> None:
        rich.print(f"[bold {color}]" + "BioHub: " + " ".join(msgs) + f"[/bold {color}]")

    @staticmethod
    def commandPrint(*msgs) -> None:
        Process.richPrint(*msgs, color = "bright_green")

    @staticmethod
    def biohubPrint(*msgs) -> None:
        Process.richPrint(*msgs, color = "bright_yellow")


    #  Getters__________________________________________________________________________________________________________


    @property
    def temporalDirectory(self) -> Path:
        return Path(self.entity.path, "files/tmp")



    @property
    def defaultOutlines(self) -> dict:

        """Outlines del proceso y de los outputs. Diseñado para leer solo una vez"""

        aux = {"process" : set(),
               "output"  : set()}

        try: frameworkInfo = json.load(open(f"{APPS_DIRECTORY}/{self.framework}/common.json"))
        except FileNotFoundError: frameworkInfo = {}

        for info in (self.jsonInfo, frameworkInfo):

            if "outlines" in info:

                for element in info["outlines"]:
                    if element["route"] in (self.route, "common"):
                        for keyWord in ("process", "output"):

                            try: aux[keyWord] |= set(element[keyWord])
                            except KeyError: pass

        return aux



    @property
    def defaultOutputOutlines(self) -> set:

        """Outlines por defecto para los ficheros de salida del proceso"""

        return self.defaultOutlines["output"]



    @property
    def defaultProcessOutlines(self) -> set:

        """Outlines por defecto para el proceso"""

        return self.defaultOutlines["process"]


#%%  Run methods____________________________________________________________________________________________________


    def run(self,
            options: dict = {},
            inputs: dict = {},
            outputOutlines: set = set(),
            processOutlines: set = set(),
            **extraAttrs) -> dict:

        timeStart = datetime.now()

        #  1. Seteando las opciones
        options = self._setOptions(**options)


        #  2. Seteando los inputs
        inputs = self._setInputs(**inputs)

        #  Si no se han seteado los inputs correctamente, devuelve un diccionario vacío
        if not inputs: return {}

        #  3. Seteando los outputs
        outputs = self._setOutputs(options = options,
                                   inputs = inputs,
                                   outputOutlines = outputOutlines,
                                   **extraAttrs)

        #  4. Aplicamos los condicionales para eliminar aquellos que no cumplan la condición
        inputs, outputs, options = self._applyEvalSentences(inputs = inputs,
                                                            outputs = outputs,
                                                            options = options,
                                                            **extraAttrs)

        #  5. Eliminamos los elementos condicionales no resueltos satisfactoriamente
        inputs, outputs, options = self._purgeConditionals(inputs = inputs,
                                                           outputs = outputs,
                                                           options = options)

        #  6. Definiendo el proceso
        process = self._setProcess(inputs = inputs,
                                  outputs = outputs,
                                  options = options,
                                  processOutlines = processOutlines,
                                  **extraAttrs)

        #  Si no se espera un duplicado, chequear si existe un proceso con outputs existentes
        #  que satisfaga el proceso que se demanda
        #  Si encuentra un duplicado, retornará los outputs del proceso duplicado. Si no encuentra
        #  nada, el proceso se ejecuta de forma normal
        if not self.duplicate:

            #  7. Buscando duplicados
            processDuplicated = self.findDuplicatedProcesses(process)

            #  8. Retornando los outputs del duplicado
            if processDuplicated:
                return self.extractOutputsFromProcess(processDuplicated[0]) #  TODO Implementar el retorno de outputs de procesos duplicados

        #  9. Ejecución del proceso
        self._runProcess(inputs = inputs,
                         outputs = outputs,
                         options = options)

        #  10. Mover los archivos resultado del directorio temporal a la carpeta
        self._moveFiles(outputs)

        #  11. Chequear los resultados del proceso
        allRight = self._checkStatus(process = process,
                                     outputs = outputs)

        if not allRight:
            return {}

        if self.save:

            #  12. Se añade la duración del proceso
            process = self._addDuration(process, datetime.now())

            #  13. Guardar en la entidad tanto el proceso como los outputs
            self._saveRecord(process = process,
                             outputs = outputs)

        #  14. Retornar los outputs
        return self.extractOutputs(process)


    #%%  1. Set options_________________________________________________________________________________________________


    @property
    def defaultOptions(self) -> dict:

        """Get default options for common route and specfic route from conf/apps/<tool>.yaml"""

        auxDefaultOptions = {}

        try: allOptions = self.jsonInfo["options"]
        except KeyError: allOptions = []

        for element in allOptions:

            if element["route"] in ("common", self.route):

                if element["role"] == "threads":
                    element["value"] = self.threads

                elif element["role"] == "outputDirectory":
                    element["value"] = self.temporalDirectory

                auxDefaultOptions[element["role"]] = Option(**element)

        return auxDefaultOptions



    def _setOptions(self, **options) -> dict:

        """Seteo de opciones
        Se buscan las opciones por defecto. Cualquier opción indicada por el usuario eliminará la opción por
        defecto correspondiente si es necesario"""

        auxOptions = {}

        count = 1

        for key, value in options.items():

            if isinstance(value, Option): #  El usuario a seteado la opción con el Wrapper
                options[value.role] = value

            else: #  El usuario ha indicado la opción con el estilo <name> : <value>
                options[f"unknown_{count}"] = Option(role = f"unknown_{count}",
                                                     name = key,
                                                     value = value)
                count += 1



        rolesToDel = []
        for defaultRole, defaultOption in self.defaultOptions.items():


            if not any([defaultOption.name in [userOption.name for userOption in options.values()],
                        defaultOption.alternativeName in [userOption.name for userOption in options.values()]]):

                auxOptions[defaultRole] = defaultOption


            else:
                for userRole, userOption in options.items():
                    if any([defaultOption.name == userOption.name, defaultOption.alternativeName == userOption.name]):

                        userOption._role = defaultOption.role
                        userOption._alternativeName = defaultOption.alternativeName

                        options[defaultRole] = userOption
                        rolesToDel.append(userRole)

        for roleToDel in rolesToDel:
            del options[roleToDel]

        auxOptions.update(options)

        return auxOptions


    #%%  2. Set inputs__________________________________________________________________________________________________


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

        inputs = self._createUserInputs(**inputs)

        inputs = self._mergeInputs(inputs, self.defaultInputs)

        inputs = self._createPendingInputs(**inputs)

        if any(input is None for input in inputs.values()):
            inputs = {}

        return inputs



    def _createUserInputs(self, **inputs):

        auxInputs = {}


        for role, input in inputs.items():

            if isinstance(input, Input):
                auxInputs[role] = input

            elif isinstance(input, File):
                auxInputs[role] = Input(role = role,
                                        biohubFile = input,
                                        pathPrefix = self.entity.path)

            elif isinstance(input, (Path, str)):
                auxInputs[role] = Input(role = role,
                                        biohubFile = verifyPath(input))

            else: pass

        return auxInputs


    # TODO revisar la no creación de cosas
    def _mergeInputs(self, inputs: dict, defaultInputs: dict) -> dict:

        auxInputs = {}

        for role, defaultInput in defaultInputs.items():

            if role in inputs: #  El usuario ha definido el input

                #  Si existe un prefijo para el input y el usuario no lo ha definido previamente (via Wrapper)
                if defaultInput.name and not inputs[role].name:
                    inputs[role]._name = defaultInput.name

                auxInputs[role] = inputs[role] #  Cargamos el input

            #  Si no ha definido el input
            else: auxInputs[role] = defaultInput

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
                return candidates[0]

            else:
                optimalFieldView = optimalFieldView[:-1]

            if len(optimalFieldView) == 0: break

        return None


    #%%  3. Set outputs_________________________________________________________________________________________________


    @property
    def defaultOutputs(self) -> dict:

        auxDefaultOutputs = {}

        try: allOutputs = self.jsonInfo["outputs"]
        except KeyError: allOutputs = []

        for element in allOutputs:

            if element["route"] in ("common", self.route):

                element["temporal"] = str(self.temporalDirectory) + "/" + element["temporal"]

                try: element["outlines"] = set(element["outlines"])
                except KeyError: element["outlines"] = set()

                auxDefaultOutputs[element["role"]] = Output(**element)

        return auxDefaultOutputs



    def _setOutputs(self,
                    inputs: dict = {},
                    options: dict = {},
                    outputOutlines: set = set(),
                    **extraAttrs) -> dict:

        auxOutputs = {}

        for role, output in self.defaultOutputs.items():

            #  Update file outlines
            output.outlines = self.defaultOutputOutlines | output.outlines | outputOutlines

            if output.evalPending:
                auxOutputs[role] = output

            else:
                auxOutputs[role] = self._createOutput(output, **extraAttrs)

        return auxOutputs


    def _createOutput(self, output: Output, **extraAttrs) -> Output:

        file = File(path = Path(f"files/{File().newId()}{output.extension}"),
                    outlines = output.outlines,
                    **extraAttrs)

        output.biohubFile = file
        output.pathPrefix = self.entity.path

        return output



    #%%  4. Eval sentences______________________________________________________________________________________________


    def _applyEvalSentences(self,
                            inputs: dict = {},
                            outputs: dict = {},
                            options: dict = {},
                            **extraAttrs) -> tuple:

        count = True
        while count:

            count = 0

            for section in options, inputs, outputs: #  Para cada sección que puede variar
                for role, wrap in section.items(): #  Para cada elemento
                    if wrap.evalPending: #  Si tiene sentencias que evaluar

                        for attr in wrap.evalAttributes: #  Para cada atributo que puede tener una sentencia

                            value = getattr(wrap, attr)

                            if isinstance(value, str) and "eval##" in value:

                                sentence = "->" + value.split("->")[1].split("<-")[0] + "<-"

                                try:

                                    result = evalSentence(sentence[2:-2],
                                                          entity = self.entity,
                                                          inputs = inputs,
                                                          outputs = outputs,
                                                          options = options,
                                                          self = self)

                                except (NameError, AttributeError, KeyError, IndexError): break

                                #  Si la sentencia es toda la expresión (puede generar un dato diferente a str)
                                if len(sentence) == len(value):
                                    value = result

                                else: #  Si es una cadena más larga, se remplaza la sentencia por el resultado
                                    value = value.replace(sentence, str(result))

                                #  Actualización del valor en el wrap
                                setattr(wrap, attr, value)

                                if not wrap.evalPending and wrap.condition: #  Si no quedan más sentencias por evaluar

                                    #  Podemos crear el Output completo
                                    if isinstance(wrap, Output):
                                        outputs[role] = self._createOutput(wrap, **extraAttrs)

                                    #  Podemos crear el Input completo
                                    elif isinstance(wrap, Input): inputs[role] = self._createInput(wrap)


                        else: count += 1 #  Añadimos una señal de que algo se ha conseguido

        return inputs, outputs, options


    #%%  5. Purge conditionals__________________________________________________________________________________________


    def _purgeConditionals(self,
                           inputs: dict = {},
                           outputs: dict = {},
                           options: dict = {}):

        aux = {"inputs"  : {},
               "outputs" : {},
               "options" : {}}

        for field, section, dataType in zip(aux.keys(), (inputs, outputs, options), (Input, Output, Option)):

            aux[field] = {key: value for key, value in section.items() \
                                     if isinstance(value, dataType) and value.condition == True}
        return aux["inputs"], aux["outputs"], aux["options"]


    #%%  6. Define process______________________________________________________________________________________________


    def _setProcess(self,
                    inputs: dict = {},
                    outputs: dict = {},
                    options: dict = {},
                    processOutlines: set = set(),
                    **extraAttrs):

        process = copy.deepcopy(self)

        #  Cambiamos el nombre del tag del elemento XML
        process._xmlElement.tag = "process"

        for extraAttr, value in extraAttrs.items():
            setattr(process, extraAttr, value)

        process.outlines = self.defaultProcessOutlines | processOutlines

        outputIds = {output.id for output in outputs.values()}
        for output in outputs.values():
            output = outputIds - {output.id}

        process.inputs = inputs

        process.outputs = outputs

        process.options = {key : value for key, value in options.items() if value.role not in DEFAULT_EXCLUDED_OPTIONS}

        return process


    #%%  7. Find duplicated processes___________________________________________________________________________________


    def findDuplicatedProcesses(self, process) -> list:

        aux = []
        for auxProcess in self.entity.processes.values():

            if process == auxProcess:
                aux.append(auxProcess)

        return aux


    #%%  8. Extract duplicated outputs__________________________________________________________________________________


    def extractOutputs(self, process) -> dict:

        if not hasattr(process, "entity"):
            process.entity = self.entity

        return {role : output.biohubFile for role, output in process.outputs.items()}


    #%%  9. Run process_________________________________________________________________________________________________


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

        if not aux: aux = DEFAULT_SENTENCE

        return aux



    def _runProcess(self,
                    inputs: dict = {},
                    outputs: dict = {},
                    options: dict = {}) -> None:

        self._createTemporalDirectory()

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

        if self.type == "system":

            self.runSystemPackage(sentence)

        elif self.type == "anaconda":

            self.runCondaPackage(sentence)

        elif self.type == "singularity":

            self.runSingularityPackage(sentence)

        else: pass


    #%%  10. Move files_________________________________________________________________________________________________


    def _moveFiles(self,
                   outputs: dict) -> None:

        self._transferTemporalFiles(outputs)

        self._deleteTemporalDirectory()


    def _transferTemporalFiles(self, outputs: dict) -> None:

        for output in outputs.values():

            self.runCommand(f"mv",
                            f"{output.temporal}",
                            f"{output.path}")


    def _deleteTemporalDirectory(self) -> None:

        self.runCommand(f"rm -rf {self.temporalDirectory}")


    #%%  11. Check status_______________________________________________________________________________________________


    def _checkStatus(self, process = None, outputs: dict = {}) -> bool:

        for output in outputs.values():

            if not Path(output.path).exists(): return False

        return True


    #%%  12. Add process duration_______________________________________________________________________________________


    def _addDuration(self, process, date):

        process.duration = date - process.date

        return process


    #%%  13. Save record________________________________________________________________________________________________


    def _saveRecord(self,
                    process = None,
                    outputs: dict = {}) -> None:

        self.entity.addProcess(process)

        for output in outputs.values():

            self.entity.addFile(output.biohubFile)

        self.entity.save()

        process.entity = self.entity




    #%%  Comparator


    def __eq__(self, other: object) -> bool:

        toCompare = ["framework", "tool", "env", "route",
                     "options", "inputs"]

        for attr in toCompare:

            if getattr(self, attr) != getattr(other, attr):
                return False

        return True

