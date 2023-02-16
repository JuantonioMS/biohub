from biohub.process import ProcessStoS
from biohub.process.align import Align


class Blastn(Align, ProcessStoS):

    def _coreProcess(self,
                     inputs: dict = {},
                     outputs: dict = {},
                     options: dict = {}) -> None:

        self.runCondaPackage("makeblastdb",
                             str(inputs["database"]),
                             f"-dbtype nucl -out {self.temporalDirectory}/blast_tmp_database.db")

        self.runCondaPackage("blastn",
                             " ".join([str(element) for element in options.values()]),
                             f"-db {self.temporalDirectory}/blast_tmp_database.db",
                             str(inputs["query"]),
                             f"-out {self.temporalDirectory}/blast_result")