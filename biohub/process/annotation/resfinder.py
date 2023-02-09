from biohub.process import ProcessStoS
from biohub.process.annotation import Annotation

from biohub.utils import Output

class Resfinder(Annotation, ProcessStoS):


    def _coreProcess(self,
                     inputs: dict = {},
                     outputs: dict = {},
                     options: str = "") -> None:

        self.runCondaPackage("run_resfinder.py",
                             f"-ifa {inputs['-ifa'].path}",
                             options,
                             f"-o {self.temporalDirectory}")
