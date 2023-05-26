from pathlib import Path

from biohub.storage import File
from biohub.process.wrapper import Output


class Outputs:


    @property
    def defaultOutputOutlines(self) -> set:

        """Outlines por defecto para los ficheros de salida del proceso"""

        return self.defaultOutlines["output"]


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

        self.logger.info(f"Process {self.id} :: OUTPUTS :: Creating output {output}; role {output.role}")

        return output