import json
import logging

from pathlib import Path

from biohub.conf.general.constant import DEFAULT_PROCESS_TEMPORAL_NAME, DEFAULT_CLI_SEPARATOR


APPS_DIRECTORY = Path(Path(Path(__file__).parent, "../../conf"), "apps")

class Properties:


    @property
    def _CLI_SEPARATOR_OPTIONS(self) -> str:

        try: return self.jsonInfo["implementation"]["cliDetails"]["optionsSeparator"]
        except KeyError: return DEFAULT_CLI_SEPARATOR


    @property
    def _CLI_SEPARATOR_INPUTS(self) -> str:

        try: return self.jsonInfo["implementation"]["cliDetails"]["inputsSeparator"]
        except KeyError: return DEFAULT_CLI_SEPARATOR


    @property
    def _CLI_SEPARATOR_OUTPUTS(self) -> str:

        try: return self.jsonInfo["implementation"]["cliDetails"]["outputsSeparator"]
        except KeyError: return DEFAULT_CLI_SEPARATOR


#%%  TEMPORAL DIRECTORY_________________________________________________________________________________________________


    @property
    def temporalDirectory(self) -> Path:
        return Path(self.entity.path, f"files/{DEFAULT_PROCESS_TEMPORAL_NAME}")


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
    def jsonInfo(self) -> dict:

        try: return json.load(open(f"{APPS_DIRECTORY}/{self.framework}/{self.tool}.json"))
        except FileNotFoundError: return {}