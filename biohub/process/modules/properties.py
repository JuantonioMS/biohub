import json
import logging

from pathlib import Path

from biohub.conf.core.constants.process import PROCESS_DEFAULT_TEMPORAL_DIRECTORY_NAME, \
                                               PROCESS_DEFAULT_SEPARATOR_CLI


APPS_DIRECTORY = Path(Path(Path(__file__).parent, "../../conf"), "apps")

class Properties:


    @property
    def _CLI_SEPARATOR_OPTIONS(self) -> str:

        try: return self.jsonInfo["implementation"]["cliDetails"]["optionsSeparator"]
        except KeyError: return PROCESS_DEFAULT_SEPARATOR_CLI


    @property
    def _CLI_SEPARATOR_INPUTS(self) -> str:

        try: return self.jsonInfo["implementation"]["cliDetails"]["inputsSeparator"]
        except KeyError: return PROCESS_DEFAULT_SEPARATOR_CLI


    @property
    def _CLI_SEPARATOR_OUTPUTS(self) -> str:

        try: return self.jsonInfo["implementation"]["cliDetails"]["outputsSeparator"]
        except KeyError: return PROCESS_DEFAULT_SEPARATOR_CLI


#%%  TEMPORAL DIRECTORY_________________________________________________________________________________________________


    @property
    def temporalDirectory(self) -> Path:
        return Path(self.entity.path, f"files/{PROCESS_DEFAULT_TEMPORAL_DIRECTORY_NAME}")


#%%  OUTLINES___________________________________________________________________________________________________________


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


#%%  JSON INFO EXTRACTION_______________________________________________________________________________________________


    @property
    def jsonFile(self) -> str:
        return f"{APPS_DIRECTORY}/{self.framework}/{self.tool}.json"


    @property
    def jsonInfo(self) -> dict:

        try: return json.load(open(self.jsonFile, "r"))
        except FileNotFoundError: return {}