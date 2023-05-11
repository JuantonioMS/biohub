from biohub.process import ProcessStoS
from biohub.process.apps.align import Align


class TBlastn(Align, ProcessStoS):

    def _coreProcess(self,
                     inputs: dict = {},
                     outputs: dict = {},
                     options: dict = {}) -> None:

        self.runCondaPackage("makeblastdb",
                             str(inputs["database"]),
                             f"-dbtype nucl -out {self.temporalDirectory}/blast_tmp_database.db")

        self.runCondaPackage("tblastn",
                             " ".join([str(element) for element in options.values()]),
                             f"-db {self.temporalDirectory}/blast_tmp_database.db",
                             str(inputs["query"]),
                             f"-out {self.temporalDirectory}/blast_result")