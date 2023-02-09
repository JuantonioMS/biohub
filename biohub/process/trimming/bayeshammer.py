from biohub.process import ProcessStoS
from biohub.process.trimming import Trimming
from biohub.utils import readYaml

class BayesHammer(Trimming, ProcessStoS):

    def _moveFiles(self, outputs: dict) -> None:

        mask = {"forward" : "left reads",
                "reverse" : "right reads",
                "single"  : "single reads"}

        for role in outputs:
            outputs[role]._temporal = readYaml(f"{self.temporalDirectory}/corrected/corrected.yaml")[0][f"{mask[role]}"][0]

            output = outputs[role]

            self.runCommand(f"mv",
                            f"{output.temporal}",
                            f"{self.entity.path}/{output.path}")

        self._deleteTemporalDirectory()