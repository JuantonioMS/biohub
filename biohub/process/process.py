from xml.etree import ElementTree as ET
from pathlib import Path
import subprocess
from datetime import datetime
import rich
from typing import Union, Any


import copy

from biohub.utils import BioHubClass
from biohub.utils import verifyPath, readYaml, evalSentence
from biohub.utils.wrapper import Input, Output, Option

from biohub.file import File


CONFDIRECTORY = Path(Path(__file__).parent, "../conf")

APPSDIRECTORY = Path(CONFDIRECTORY, "apps")

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




    def __setattr__(self, attr: str, value: Any) -> None:

        #  Atributos que son atributos del elemento XML
        if attr == "duration":

            self._xmlElement.attrib[attr] = str(value)

        else: super().__setattr__(attr, value)







    def __getattribute__(self, attr: str):

        """
        Modificado para retornar de forma diferente los inputs y outputs como objectos Files
        """

        if attr in super().__getattribute__("processSpecialAttrs"):

            files = self._xmlElement.find(attr)

            aux = {}
            if files is not None:
                for file in files:

                    if "/" in file.text: #  Si es un fichero externo se retorna el Path
                        aux[file.text] = Path(file.text)
                    else: #  Si es un fichero BioHub se retorna el objeto

                        if file.text in self.entity.files:
                            aux[file.text] = self.entity.files[file.text]

                        else: #  Si el fichero ya no existe en la fuente, retorna None
                            aux[file.text] = None

            return aux

        if attr == "duration":
            try: return self._xmlElement.attrib[attr]
            except KeyError: return ""

        else: return super().__getattribute__(attr)


    #  _________________________CLI Run Methods_________________________


    def runCommand(self, *args, captureOutput: bool = False) -> None:

        """
        Ejecuta comandos del sistema. Retorna el valor de ejecución resultante. Suele ser 0 el valor de todo correcto.
        Tiene la opción de capturar la salida si captureOuput es True y retorna el output.
        """

        Process.commandPrint(*args)
        output = subprocess.run(" ".join(args),
                                shell = True,
                                executable = "/bin/bash",
                                capture_output = captureOutput)

        if captureOutput:
            return output.returncode, output.stdout.encode("UTF8")

        else:
            return output.returncode



    def runCondaPackage(self, *args, env: str = None, captureOutput: bool = False) -> None:

        """
        Ejecuta comandos recogidos en entornos conda de forma similar al método runCommand
        """

        #  Búsqueda del shell de conda instalado en el sistema
        condaShell = "/".join(subprocess.getoutput("which conda").split("/")[:-2])

        if not env:
            env = self.env

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
    def toolYamlInfo(self) -> dict:
        return readYaml(f"{APPSDIRECTORY}/{self.framework}/{self.tool}.yaml")

    @property
    def frameworkYamlInfo(self) -> dict:
        return readYaml(f"{APPSDIRECTORY}/{self.framework}/common.yaml")

    @property
    def specialAttrs(self) -> set:
        return super().specialAttrs.union({"framework", "tool", "route", "duration",
                                           "env", "options", "inputs", "outputs"})

    @property
    def processSpecialAttrs(self) -> set:
        return {"inputs", "outputs"}


    @property
    def framework(self) -> str:

        """Marco de trabajo del proceso (ej. Unicycler -> assembly)"""

        framework = self.__class__.__base__.__name__.lower()

        self.framework = framework

        return framework



    @property
    def tool(self) -> str:

        """Nombre de la herramienta del proceso (ej. Unicycler -> unicycler)"""


        tool = self.__class__.__name__.lower()

        self.tool = tool

        return tool



    @property
    def env(self) -> str:

        """Nombre del entorno de conda que tiene la herramienta (ej. Unicycler -> biohub.unicycler)
        Si no existe un entorno para esa herramienta, se retorna 'base'"""

        try: auxEnv = self.toolYamlInfo["info"]["envs"]
        except KeyError: auxEnv = "base" #  Si no está definido

        self.env = auxEnv

        return auxEnv



    @property
    def route(self) -> str:

        """Ruta por defecto del proceso. Si no está especificada, por defecto es common"""

        try: auxRoute = self.toolYamlInfo["info"]["defaultRoute"]
        except KeyError: auxRoute = "common" #  Si no está definido

        self.route = auxRoute

        return auxRoute



    @property
    def temporalDirectory(self) -> Path:
        return Path(self.entity.path, "files/tmp")



    @property
    def defaultOutlines(self) -> dict:

        """Outlines del proceso y de los outputs. Diseñado para leer solo una vez"""

        aux = {"process" : set(),
               "output"  : set()}


        if "outlines" in self.toolYamlInfo:

            for route in ("common", self.route):
                for keyWord in aux.keys():

                    try: aux[keyWord] |= set(self.toolYamlInfo["outlines"][route][keyWord])
                    except KeyError: pass

        if "outlines" in self.frameworkYamlInfo:

            for keyWord in self.frameworkYamlInfo["outlines"]["common"]:
                aux[keyWord] |= set(self.frameworkYamlInfo["outlines"]["common"][keyWord])

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
        inputs, outputs, options = self._applyEvalSentences(entity = self.entity,
                                                            inputs = inputs,
                                                            outputs = outputs,
                                                            options = options)

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
        return self._extractOutputs(outputs)


    #%%  1. Set options_________________________________________________________________________________________________


    @property
    def defaultOptions(self) -> dict:

        """Get default options for common route and specfic route from conf/apps/<tool>.yaml"""

        auxDefaultOptions = {}

        #  Get all options for process
        try: allOptions = self.toolYamlInfo["options"]
        except KeyError: allOptions = {}

        #  Select common route options
        for route in ("threads", "common", self.route):

            #  Step 1. Threads options
            #  Step 2. Common route options
            #  Step 3. Specific route options

            try:

                for role, optionInfo in allOptions[route].items():

                    if route == "threads":
                        auxDefaultOptions[optionInfo["name"]] = Option(role = role,
                                                                       value = self.threads,
                                                                       **optionInfo)

                    else:
                        auxDefaultOptions[optionInfo["name"]] = Option(role = role,
                                                                       **optionInfo)

            except KeyError: pass

        return auxDefaultOptions



    def _setOptions(self, **options) -> dict:

        """Seteo de opciones
        Se buscan las opciones por defecto. Cualquier opción indicada por el usuario eliminará la opción por
        defecto correspondiente si es necesario"""

        auxOptions = {}

        for key, value in options.items():

            if isinstance(value, Option): #  El usuario a seteado la opción con el Wrapper
                options[value.name] = value

            else: #  El usuario ha indicado la opción con el estilo <name> : <value>
                options[key] = Option(name = key, value = value)


        for name, option in self.defaultOptions.items():

            if not any([option.name in list(options.keys()), option.alternative in list(options.keys())]):
                auxOptions[name] = option

        auxOptions.update(options)

        return auxOptions


    #%%  2. Set inputs__________________________________________________________________________________________________


    @property
    def defaultInputs(self):

        auxDefaultInputs = {}

        try: allInputs = self.toolYamlInfo["inputs"]
        except KeyError: allInputs = {}

        for route in ("common", self.route):

            #  Step 1. Common route inputs
            #  Step 2. Specific route inptus

            try:

                for role, inputInfo in allInputs[route].items():

                    auxDefaultInputs[role] = inputInfo

            except KeyError: pass

        return auxDefaultInputs



    def _setInputs(self, **inputs) -> dict:

        #  Merge user inputs with default inputs

        inputs = self._createUserInputs(**inputs)

        inputs = self._mergeInputs(inputs, self.defaultInputs)

        inputs = self._createPendingInputs(**inputs)

        if any(input is None for input in inputs.values()):
            return {}
        else:
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

        for role, input in defaultInputs.items():

            if role in inputs: #  El usuario ha definido el input

                #  Si existe un prefijo para el input y el usuario no lo ha definido previamente (via Wrapper)
                if "inputName" in input and not hasattr(inputs[role], "_inputsName"):
                    setattr(inputs[role], "_inputName", input["inputName"]) #  Setea el inputName

                auxInputs[role] = inputs[role] #  Cargamos el input

            #  Si no ha definido el input
            else: auxInputs[role] = input

        return auxInputs



    def _createPendingInputs(self, **inputs) -> dict:

        auxInputs = {}

        for role, inputInfo in inputs.items():

            if isinstance(inputInfo, Input): auxInputs[role] = inputInfo

            else:

                if not "condition" in inputInfo:
                    auxInputs[role] = self._createInput(role, inputInfo)

                else:
                    auxInputs[role] = inputInfo

        return auxInputs



    def _createInput(self,
                     role: str,
                     inputInfo: dict) -> Union[Input, None]:

        input = self._selectInput(inputInfo)

        if input:

            input = Input(role = role,
                          biohubFile = input,
                          pathPrefix = self.entity.path,
                          **inputInfo)

        return input



    def _selectInput(self, inputInfo: dict) -> any:

        required, optimal = {}, {}

        for field in inputInfo:

            #  No son elementos que podamos buscar
            if field not in ("inputName", "condition"):

                try: required[field] = set(inputInfo[field]["required"])
                except KeyError: pass

                try: optimal[field] = inputInfo[field]["optimal"]
                except KeyError: pass


        optimalFieldView = [(field, value) for field in optimal for value in optimal[field]]
        while optimalFieldView:

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

        return None



    #%%  3. Set outputs_________________________________________________________________________________________________


    @property
    def defaultOutputs(self):

        auxDefaultOutputs = {}

        try: allOutputs = self.toolYamlInfo["outputs"]
        except KeyError: allOutputs = {}


        for route in ("common", self.route):

            #  Step 1. Common route inputs
            #  Step 2. Specific route inptus

            try:

                for role, outputInfo in allOutputs[route].items():

                    auxDefaultOutputs[role] = outputInfo

            except KeyError: pass

        return auxDefaultOutputs



    def _setOutputs(self,
                    inputs: dict = {},
                    options: dict = {},
                    outputOutlines: set = set(),
                    **extraAttrs) -> dict:

        outputs = self._createOutputs(outputOutlines = outputOutlines,
                                      **extraAttrs)

        return outputs



    def _createOutputs(self,
                       outputOutlines: set = set(),
                       **extraAttrs) -> dict:

        auxOutputs = {}

        for role, outputInfo in self.defaultOutputs.items():

            if not any(["eval##" in outputInfo["temporal"],
                        "eval##" in outputInfo["extension"],
                        "condition" in outputInfo]):

                auxOutputs[role] = self._createOutput(role,
                                                      outputInfo,
                                                      outputOutlines = outputOutlines,
                                                      **extraAttrs)

            else: auxOutputs[role] = outputInfo

        return auxOutputs



    def _createOutput(self,
                      role: str,
                      outputInfo: dict,
                      outputOutlines: set = set(),
                      **extraAttrs) -> Output:

        output = File(path = Path(f"files/{File().newId()}{outputInfo['extension']}"),
                      outlines = self.defaultOutputOutlines |\
                                 (set(outputInfo["outlines"]) if "outlines" in outputInfo else set()) |\
                                 outputOutlines if isinstance(outputOutlines, set) else set(outputOutlines),
                      **extraAttrs)

        return Output(biohubFile = output, role = role, **outputInfo)


    #%%  4. Eval sentences______________________________________________________________________________________________


    def _applyEvalSentences(self,
                            entity: str = None,
                            inputs: dict = {},
                            outputs: dict = {},
                            options: dict = {}) -> tuple:

        count = True
        while count:

            count = 0

            #  Sección de las opciones
            for optionName, option in options.items():

                if any([isinstance(option.condition, str), False if not isinstance(option.value, str) else "eval##" in option.value]):
                    for word in ("condition", "value"):

                        if isinstance(info := getattr(option, word), str) and "eval##" in info:
                            try:

                                result = evalSentence(info,
                                                    entity = entity,
                                                    inputs = inputs,
                                                    outputs = outputs,
                                                    options = options,
                                                    self = self)

                                setattr(option, f"_{word}", result)

                            except (NameError, AttributeError, KeyError, IndexError): break

                    else:
                        count += 1


            #  Sección de los inputs
            for inputRole, inputInfo in inputs.items():

                if isinstance(inputInfo, dict): #  Está pendiente de definir el Input
                    for word in ("inputName", "condition"):

                        if word in inputInfo and "eval##" in inputInfo[word]:

                            try:
                                result = evalSentence(inputInfo[word],
                                                      entity = entity,
                                                      inputs = inputs,
                                                      outputs = outputs,
                                                      options = options,
                                                      self = self)

                                inputInfo[word] = result

                            except (NameError, AttributeError, KeyError, IndexError): break

                    else:
                        inputs[inputRole] = self._createInput(inputRole, inputInfo)
                        count += 1

            #  Sección de los outputs
            for outputRole, outputInfo in outputs.items():

                if isinstance(outputInfo, dict): #  Está pendiente de definir el Output
                    for word in ("temporal", "condition", "extension"):

                        if word in outputInfo and "eval##" in outputInfo[word]:

                            try:
                                result = evalSentence(outputInfo[word],
                                                      entity = entity,
                                                      inputs = inputs,
                                                      outputs = outputs,
                                                      options = options,
                                                      self = self)

                                outputInfo[word] = result

                            except (NameError, AttributeError, KeyError, IndexError): break

                    else:
                        outputs[outputRole] = self._createOutput(outputRole, outputInfo)
                        count += 1

        return inputs, outputs, options


    #%%  5. Purge conditionals__________________________________________________________________________________________


    def _purgeConditionals(self,
                           inputs: dict = {},
                           outputs: dict = {},
                           options: dict = {}):

        auxInputs = {key: value for key, value in inputs.items() \
                                if isinstance(value, Input) and value.condition == True}
        auxOutputs = {key: value for key, value in outputs.items() \
                                 if isinstance(value, Output) and value.condition == True}
        auxOptions = {key: value for key, value in options.items() \
                                 if isinstance(value, Option) and value.condition == True}

        return auxInputs, auxOutputs, auxOptions


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

        process.inputs = {input.id for input in inputs.values()}

        process.outputs = {output.id for output in outputs.values()}

        process.options = {str(option) for option in options.values() if option.role != "threads"}

        return process


    #%%  7. Find duplicated processes___________________________________________________________________________________


    def findDuplicatedProcesses(self, process) -> list:

        aux = []
        for auxProcess in self.entity.processes.values():

            if process == auxProcess:
                aux.append(auxProcess)

        return aux


    #%%  8. Extract duplicated outputs__________________________________________________________________________________


    def extractOutputsFromProcess(self, process) -> dict:
        return process.outputs


    #%%  9. Run process_________________________________________________________________________________________________


    @property
    def instruct(self) -> str:

        for route in (self.route, "common"):

            try: return self.toolYamlInfo["execution"]["instruct"][route]
            except KeyError: continue

        return self.tool


    @property
    def sentence(self) -> str:

        for route in (self.route, "common"):

            try: return self.toolYamlInfo["execution"]["sentence"][route]
            except KeyError: continue

        return "PRinstruct PRinputs PRoptions"


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
                     options: str = "") -> None:

        self.runCondaPackage(self.sentence.replace("PRinstruct", self.instruct)\
                                          .replace("PRoptions", " ".join([str(element) for element in options.values()]))\
                                          .replace("PRinputs", " ".join([str(element) for element in inputs.values()]))\
                                          .replace("PRoutputs", " ".join([str(element) for element in outputs.values()])))


    #%%  10. Move files_________________________________________________________________________________________________


    def _moveFiles(self,
                   outputs: dict) -> None:

        for output in outputs.values():

            self.runCommand(f"mv",
                            f"{self.temporalDirectory}/{output.temporal}",
                            f"{self.entity.path}/{output.path}")

        self._deleteTemporalDirectory()



    def _deleteTemporalDirectory(self) -> None:

        self.runCommand(f"rm -rf {self.temporalDirectory}")


    #%%  11. Check status_______________________________________________________________________________________________


    def _checkStatus(self, process = None, outputs: dict = {}) -> bool:

        for output in outputs.values():

            path = Path(self.entity.path, output.biohubFile.path)

            if not path.exists(): return False

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

        ids = [output.id for output in outputs.values()]

        for output in outputs.values():

            output.biohubFile.links = {bhId for bhId in ids if bhId != output.id}

            self.entity.addFile(output.biohubFile)

        self.entity.save()


    #%%  14. Extract outputs____________________________________________________________________________________________


    def _extractOutputs(self,
                        outputs: dict) -> dict:

        return {role : output.biohubFile for role, output in outputs.items()}


    #%%


    #%%  Comparator


    def __eq__(self, other: object) -> bool:

        toCompare = ["framework", "tool", "env", "route",
                     "options", "inputs"]

        for attr in toCompare:

            if getattr(self, attr) != getattr(other, attr):
                return False

        return True

