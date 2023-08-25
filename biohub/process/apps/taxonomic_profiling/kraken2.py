from biohub.process import ProcessStoS
from biohub.process.apps.taxonomic_profiling import TaxonomicProfiling


class Kraken2(TaxonomicProfiling, ProcessStoS):
    pass