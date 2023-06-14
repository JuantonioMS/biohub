import os
import json
from Bio.SearchIO.BlastIO.blast_xml import BlastXmlParser

from biohub.process import ProcessStoS
from biohub.process.apps.align import Align

from biohub.storage import Folder

class AlleleCaller(Align, ProcessStoS):


    def _coreProcess(self,
                     inputs: dict = {},
                     outputs: dict = {},
                     options: dict = {}) -> None:

        self.runCondaPackage("makeblastdb",
                             str(inputs["database"]),
                             f"-dbtype nucl -out {self.temporalDirectory}/blast_tmp_database.db")

        if isinstance(inputs["query"].biohubFile, Folder):
            files = [f"{inputs['query'].path}/{file}" for file in os.listdir(inputs["query"].path)]

        else:
            files = [str(inputs["query"].path)]

        result = []
        for file in files:

            self.runCondaPackage("blastn",
                                " ".join([str(option) for option in options.values()]),
                                f"-db {self.temporalDirectory}/blast_tmp_database.db",
                                f"-query {file}",
                                f"-out {self.temporalDirectory}/blast_result.xml")

            hsps = []
            for query in BlastXmlParser(f"{self.temporalDirectory}/blast_result.xml"):
                for hit in query.hits:
                    for hsp in hit.hsps:

                        hsp.identity = (hsp.ident_num - hsp.gap_num) / query.seq_len
                        hsps.append(hsp)

            hsps.sort(key = lambda x: x.identity, reverse = True)

            if hsps:
                hsp = hsps[0]
                result.append({"allele"       : hsp.query_id,
                               "identity"     : hsp.identity,
                               "bitscore"     : hsp.bitscore,
                               "bitscore_raw" : hsp.bitscore_raw,
                               "matches"      : hsp.ident_num,
                               "gaps"         : hsp.gap_num,
                               "evalue"       : hsp.evalue})

        with open(f"{self.temporalDirectory}/result.json", "w") as outfile:
            json.dump(result, outfile, indent = 4)