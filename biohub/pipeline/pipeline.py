from biohub.core.biohub_class import BioHubClass

import xml.etree.ElementTree as ET

from pathlib import Path

import json

PIPELINES_DIRECTORY = Path(Path(Path(__file__).parent, "../../conf"), "pipelines")
PIPELINE_DEFAULT_TYPE = "subject2subject"

class Pipeline(BioHubClass):


    def __init__(self,
                 xmlElement: ET.Element = ET.Element("pipeline"), #  Útil para importar
                 entity = None, #  Sujeto o proyecto
                 save: bool = True, #  Si el proceso se debe añadir o no  a la entidad
                 duplicate: bool = False, #  Si False, si se detecta un proceso completado igual, no se ejecutará
                 **attrs) -> None:

        self.entity = entity



    def minimumBuild(self) -> None:

        if self.name is None:
            self.name = self.__class__,__name__.lower()


    @property
    def jsonInfo(self) -> dict:

        try: return json.load(open(f"{PIPELINES_DIRECTORY}/{self.name}.json"))
        except FileNotFoundError: return {}


    @property
    def type(self) -> str:

        try: return self.jsonInfo["info"]["type"]
        except KeyError: return PIPELINE_DEFAULT_TYPE


    @property
    def processes(self) -> list:

        try: return self.jsonInfo["processes"]
        except KeyError: return []
        
        
    