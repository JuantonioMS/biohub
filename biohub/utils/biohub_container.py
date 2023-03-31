from pathlib import Path
from typing import Any

import xml.etree.ElementTree as ET
from xml.dom import minidom

import subprocess
from biohub.utils import BioHubClass

import logging

class BioHubContainer(BioHubClass):


    def __init__(self,
                 path = Path(),
                 **attrs) -> None:

        from biohub.file.format import Xml

        if not isinstance(path, Path):
            path = Path(path)

        self._xml = Xml(path = path)

        self.path = path.parent

        super().__init__(xmlElement = self._xml.get(tag = "metadata")[0],
                        **attrs)

        #  Si no tiene carpeta files se crea
        if not Path(self.path, "files").exists():

            subprocess.call(f"mkdir {Path(self.path, 'files')}",
                            shell = True,
                            executable = "/bin/bash")


    @property
    def logger(self):

        auxLogger = logging.Logger(f"{self.id} ({self.name})")
        auxLogger.setLevel(logging.INFO)

        terminalHandler = logging.StreamHandler()
        terminalHandler.setLevel(logging.INFO)

        containerHandler = logging.FileHandler(f"{self.path}/logging.log", encoding = "utf-8")
        containerHandler.setLevel(logging.INFO)

        globalHandler = logging.FileHandler(f"biohub_logging.log", encoding = "utf-8")
        globalHandler.setLevel(logging.INFO)

        fmt = ["[log]",
               "%(asctime)s :: %(levelname)s",
               "%(message)s",
               "%(filename)s (line %(lineno)s) :: %(name)s\n"]

        formatter = logging.Formatter("\n".join(fmt),
                                      datefmt = '%d/%b/%Y %H:%M:%S')

        globalFmt = "[log] %(asctime)s :: %(name)s :: %(levelname)s :: %(message)s :: (%(filename)s line:%(lineno)s)"
        globalFormatter = logging.Formatter(globalFmt, datefmt='%d/%b/%Y %H:%M:%S')

        containerHandler.setFormatter(formatter)
        terminalHandler.setFormatter(globalFormatter)
        globalHandler.setFormatter(globalFormatter)

        auxLogger.addHandler(containerHandler)
        auxLogger.addHandler(terminalHandler)
        auxLogger.addHandler(globalHandler)

        return auxLogger


    #  Add info_________________________________________________________________________________________________________
    def addInfoBlock(self, case: str, encased: Any) -> None:
        self._xml.get(case)[0].append(encased._xmlElement)

    def addFile(self, file): self.addInfoBlock("files", file)
    def addProcess(self, process): self.addInfoBlock("processes", process)
    def addPipeline(self, pipeline): self.addInfoBlock("pipelines", pipeline)


    #  Del info_________________________________________________________________________________________________________
    def delInfoBlock(self, case: str, encased: Any) -> None:
        self._xml.remove(case, filt = {"id" : encased.id})

    def delFile(self, file): self.delInfoBlock("file", file)
    def delProcess(self, process): self.delInfoBlock("process", process)
    def delPipeline(self, pipeline): self.delInfoBlock("pipeline", pipeline)


    #  Select info______________________________________________________________________________________________________
    def selectInfoBlock(self, case: str, **filt) -> list:

        auxFilt = {}
        for key, value in filt.items():

            if key in ("date", "comment"):              auxFilt[f"@{key}"] = value
            elif isinstance(value, (list, tuple, set)): auxFilt[f"#{key}"] = value
            else:                                       auxFilt[key]       = value

        return self._xml.get(case, filt = auxFilt)

    def selectFile(self, **filt) -> list:

        from biohub.file import File

        return [File(xmlElement = block) for block in self.selectInfoBlock("file", **filt)]

    def selectProcess(self, **filt) -> list:

        from biohub.process import Process

        return [Process(xmlElement = block) for block in self.selectInfoBlock("process", **filt)]

    def selectPipeline(self, **filt) -> list: return self.selectInfoBlock("pipeline", **filt)


    #%%  XML special tags_______________________________________________________________________________________________


    @property
    def _xmlElementTags(self) -> set: return {"name"} | super()._xmlElementTags

    @property
    def _xmlSpecialTags(self) -> set: return {"files", "processes", "pipelines"} | super()._xmlSpecialTags


    #%%  Getters built-in methods_______________________________________________________________________________________


    def __getXmlSpecialTag__(self, attr: str) -> Any:

        if attr in {"files", "processes", "pipelines"}:

            from biohub.file import File
            from biohub.process import Process

            aux = {}
            for subelement in self._xml.get(tag = attr)[0]:

                #  Creating an instance with xml info
                instance = locals()[subelement.tag.capitalize()](xmlElement = subelement, entity = self)

                #  Adding to dictionary with id as key, instance as value
                aux[subelement.find("id").text] = instance

            return aux

        else: return super().__getXmlSpecialTag__(attr)



    def __setXmlSpecialTag__(self, attr: str, value: Any) -> None:

        if attr in {"files", "processes", "pipelines"}:

            if getattr(self, attr) is None:
                ET.SubElement(self._xml.root, attr)

        else: super().__setXmlSpecialTag__(attr, value)


    #  Saving methods___________________________________________________________________________________________________


    def save(self) -> None:

        prettyXml = minidom.parseString(ET.tostring(self._xml.root)\
                                       .decode("UTF-8").replace("\n", "")\
                                       .replace("    ", ""))\
                                       .toprettyxml(indent = "    ")

        with open(self._xml.path, "wb") as biohubFile:
            biohubFile.write(prettyXml.encode("utf-8"))