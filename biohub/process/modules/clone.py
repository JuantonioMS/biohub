import copy

from biohub.conf.general.constant import DEFAULT_PROCESS_ROLES_EXCLUDED

class Clone:

    @property
    def defaultProcessOutlines(self) -> set:

        """Outlines por defecto para el proceso"""

        return self.defaultOutlines["process"]


    def _setProcess(self,
                    inputs: dict = {},
                    outputs: dict = {},
                    options: dict = {},
                    processOutlines: set = set(),
                    **extraAttrs):

        process = copy.copy(self)

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

        process.options = {key : value for key, value in options.items() if value.role not in DEFAULT_PROCESS_ROLES_EXCLUDED}

        return process