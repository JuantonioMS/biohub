from biohub.process import ProcessStoS
from biohub.process.apps.trimming import Trimming
from biohub.utils import readYaml

class BayesHammer(Trimming, ProcessStoS):

    def _transferTemporalFiles(self, outputs: dict) -> None:

        mask = {"forward" : "left reads",
                "reverse" : "right reads",
                "single"  : "single reads"}

        for role, output in outputs.items():
            output.temporal = readYaml(f"{self.temporalDirectory}/corrected/corrected.yaml")[0][f"{mask[role]}"][0]

            self.runCommand(f"mv",
                            f"{output.temporal}",
                            f"{output.path}")