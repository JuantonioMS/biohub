from pathlib import Path

import json

from biohub.conf.general.constant import DEFAULT_PROCESS_TEMPORAL_NAME

APPS_DIRECTORY = Path(Path(Path(__file__).parent, "../../conf"), "apps")

class Properties:


    @property
    def temporalDirectory(self) -> Path:
        return Path(self.entity.path, f"files/{DEFAULT_PROCESS_TEMPORAL_NAME}")


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
    def jsonInfo(self) -> dict:

        try: return json.load(open(f"{APPS_DIRECTORY}/{self.framework}/{self.tool}.json"))
        except FileNotFoundError: return {}