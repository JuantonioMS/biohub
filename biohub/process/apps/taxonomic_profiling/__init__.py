from biohub.process import Process

class TaxonomicProfiling(Process):
    pass

from biohub.process.apps.taxonomic_profiling.metaphlan import MetaPhlAn
from biohub.process.apps.taxonomic_profiling.motus2 import MOTUs2
from biohub.process.apps.taxonomic_profiling.centrifuge import Centrifuge
from biohub.process.apps.taxonomic_profiling.kraken2 import Kraken2
from biohub.process.apps.taxonomic_profiling.kraken_uniq import KrakenUniq