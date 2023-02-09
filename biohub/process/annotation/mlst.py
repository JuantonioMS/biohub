from biohub.process import ProcessStoS
from biohub.process.annotation import Annotation


class Mlst(Annotation, ProcessStoS):

    def _coreProcess(self,
                     inputs: dict = {},
                     outputs: dict = {},
                     options: str = "") -> None:


        self.runCondaPackage("mlst",
                             options,
                             f"--json {self.temporalDirectory}/{outputs['--json'].temporal}",
                             f"{inputs['genome'].path}")