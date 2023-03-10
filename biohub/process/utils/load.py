from biohub.process.utils import Utils
from biohub.utils.wrapper import Output

from biohub.file import File

class Load(Utils):

    def _mergeInputs(self, inputs: dict, defaultInputs: dict) -> dict:
        return inputs

    def _setOutputs(self,
                    options: dict = {},
                    inputs: dict = {},
                    outputOutlines: set = set(),
                    **extraAttrs) -> dict:

        outputs = {}

        for inputRole, inputInfo in inputs.items():

            outlines = {outline for outline in inputRole.split(";") if len(outline) > 1}

            output = File(**extraAttrs)
            output.path = f"files/{File().newId()}{inputInfo.suffixes}"
            output.outlines = self.defaultOutputOutlines | outputOutlines | outlines


            outputs[inputRole] = Output(temporal = inputInfo.path,
                                        role = inputRole,
                                        pathPrefix = self.entity.path,
                                        biohubFile = output)


        #  Adding links if necessary
        if len(outputs) > 1:
            links = {output.id for output in outputs.values()}

            for role in outputs:

                outputs[role].biohubFile.links = {link for link in links if link != outputs[role].id}

        return outputs



    def _runProcess(self,
                    inputs: dict = {},
                    outputs: dict = {},
                    options: dict = {}) -> None:

        pass



    def _moveFiles(self, outputs: dict) -> None:

        for output in outputs.values():

            self.runCommand(f"cp",
                            f"{output.temporal}",
                            f"{output.path}")
