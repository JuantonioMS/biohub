from xml.etree import ElementTree as ET
from pathlib import Path
from datetime import datetime, timedelta
import rich
from typing import Any

from pattern.en import singularize

from biohub.utils import BioHubClass
from biohub.utils.wrapper import Input, Output, Option
from biohub.process.modules import Commands, Properties, \
                                   Options, Inputs, Outputs, \
                                   Utils, Clone, \
                                   Implementation, Transfer, \
                                   Check, Save


APPS_DIRECTORY = Path(Path(Path(__file__).parent, "../conf"), "apps")

from biohub.conf.general.constant import DEFAULT_PROCESS_ENVIROMMENT, \
                                         DEFAULT_PROCESS_ROUTE, \
                                         DEFAULT_PROCESS_TYPE


class Process(BioHubClass,
              Commands, Properties,
              Options, Inputs, Outputs,
              Utils, Clone,
              Implementation, Transfer,
              Check, Save):

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



    def minimumBuild(self) -> None:

        if self.framework is None:
            self.framework = self.__class__.__base__.__name__.lower()

        if self.tool is None:
            self.tool = self.__class__.__name__.lower()

        if self.type is None:

            try: self.type = self.jsonInfo["info"]["type"]
            except KeyError: self.type = DEFAULT_PROCESS_TYPE


        if self.environment is None:

            try: self.environment = self.jsonInfo["info"]["environment"]
            except KeyError: self.environment = DEFAULT_PROCESS_ENVIROMMENT

        if self.route is None:

            try: self.route = self.jsonInfo["implementation"]["defaultRoute"]
            except KeyError: self.route = DEFAULT_PROCESS_ROUTE

        super().minimumBuild()


    #%%  XML section

    @property
    def _xmlElementTags(self) -> set: return {"framework", "tool", "route",
                                              "type", "environment"} | super()._xmlElementTags

    @property
    def _xmlSpecialTags(self) -> set:
        return {"duration", "inputs", "outputs", "options"} | super()._xmlSpecialTags


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


#%%  Run methods____________________________________________________________________________________________________


    def run(self,
            options: dict = {},
            inputs: dict = {},
            outputOutlines: set = set(),
            processOutlines: set = set(),
            **extraAttrs) -> dict:

        self.entity.logger.info(f"Process {self.id} :: RUN :: Process description\n\tFramework: {self.framework}\n\tTool: {self.tool}\n")

        #self._checkAppBuild()

        timeStart = datetime.now()

        #  1. Seteando las opciones
        self.entity.logger.info(f"Process {self.id} :: OPTIONS :: Setting options")
        options = self._setOptions(**options)


        #  2. Seteando los inputs
        self.entity.logger.info(f"Process {self.id} :: INPUTS :: Setting inputs")
        inputs = self._setInputs(**inputs)

        #  Si no se han seteado los inputs correctamente, devuelve un diccionario vacío
        if not inputs:
            self.entity.logger.error(f"Process {self.id} :: RUN :: Some input is not working properly")
            return {}

        #  3. Seteando los outputs
        self.entity.logger.info(f"Process {self.id} :: OUTPUTS :: Setting outputs")
        outputs = self._setOutputs(options = options,
                                   inputs = inputs,
                                   outputOutlines = outputOutlines,
                                   **extraAttrs)

        #  4. Aplicamos los condicionales para eliminar aquellos que no cumplan la condición
        self.entity.logger.info(f"Process {self.id} :: UTILS :: Applying eval sentences")
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


    #%%  Comparator


    def __eq__(self, other: object) -> bool:

        toCompare = ["framework", "tool", "env", "route",
                     "options", "inputs"]

        for attr in toCompare:

            if getattr(self, attr) != getattr(other, attr):
                return False

        return True