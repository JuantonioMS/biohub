class Annotation:
    pass

#  Sequence Type
from biohub.process.apps.annotation.mlst import Mlst

#  Functional genes
from biohub.process.apps.annotation.prokka import Prokka

#  Antibiotic Resistance Genes
from biohub.process.apps.annotation.resfinder import ResFinder
from biohub.process.apps.annotation.amrfinder import AMRFinder
from biohub.process.apps.annotation.abricate import Abricate
from biohub.process.apps.annotation.rgi import Rgi

#  Plasmids
from biohub.process.apps.annotation.plasmidfinder import PlasmidFinder
