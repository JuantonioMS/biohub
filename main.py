from biohub.utils import EntityCreator
from biohub.process.apps.utils import Load

import os
from pathlib import Path

os.system("rm -rf ./tests/material/storage")
os.system("mkdir ./tests/material/storage")

os.system("mkdir ./tests/material/storage/subjects")
os.system("mkdir ./tests/material/storage/projects")
os.system("mkdir ./tests/material/storage/databases")
os.system("mkdir ./tests/material/storage/databases/files")


from biohub.utils import EntityCreator
from biohub.process.apps.utils import Load
from biohub.process.apps.utils import LoadFolder

database = EntityCreator().createDatabase("test_database",
                                          "./tests/material/storage/databases")

LoadFolder(entity = database).run(inputs = {"multi locus" : Path("./databases/mlst")},
                                  outputOutlines = {"klebsiella pneumoniae"})
LoadFolder(entity = database).run(inputs = {"aerobactin locus" : Path("./databases/abst")},
                                  outputOutlines = {"klebsiella pneumoniae"})
LoadFolder(entity = database).run(inputs = {"colibactin locus" : Path("./databases/cbst")},
                                  outputOutlines = {"klebsiella pneumoniae"})
LoadFolder(entity = database).run(inputs = {"rmp locus" : Path("./databases/rmst")},
                                  outputOutlines = {"klebsiella pneumoniae"})
LoadFolder(entity = database).run(inputs = {"salmochelin locus" : Path("./databases/smst")},
                                  outputOutlines = {"klebsiella pneumoniae"})
LoadFolder(entity = database).run(inputs = {"yersiniabactin locus" : Path("./databases/ybst")},
                                  outputOutlines = {"klebsiella pneumoniae"})
LoadFolder(entity = database).run(inputs = {"virulence genes" : Path("./databases/virulence_genes")},
                                  outputOutlines = {"klebsiella pneumoniae"})
LoadFolder(entity = database).run(inputs = {"wzi locus" : Path("./databases/wzi")},
                                  outputOutlines = {"klebsiella pneumoniae"})

subjects = []
for index in range(10):

    subject = EntityCreator().createSubject(f"test_subject_{index}",
                                            "./tests/material/storage/subjects")

    Load(entity = subject).run(inputs = {"forward" : Path("./tests/material/files/a_forward.fq.gz"),
                                         "reverse" : Path("./tests/material/files/a_reverse.fq.gz")},
                               outputOutlines = {"illumina", "reads", "short", "raw"})

    subjects.append(subject.id)

project = EntityCreator().createProject("test_project",
                                        "./tests/material/storage/projects",
                                        subjects = subjects)

from biohub.container import Project

project = Project(path = "./tests/material/storage/projects/test_project/biohub_project.xml")

from biohub.process.apps.analysis import FastQC

FastQC(entity = project,
       threadsPerTask = 2,
       distributedMemory = True,
       memoryPerTask = "4GB").run()

from biohub.process.apps.trimming import BayesHammer

BayesHammer(entity = project,
            threadsPerTask = 10,
            distributedMemory = True).run()

from biohub.process.apps.assembly import Unicycler

Unicycler(entity = project,
          threadsPerTask = 10,
          distributedMemory = True).run()

from biohub.process.apps.analysis import Quast

Quast(entity = project,
      threadsPerTask = 2,
      distributedMemory = True,
      memoryPerTask = "4GB").run()

from biohub.process.apps.annotation import Prokka

Prokka(entity = project,
       threadsPerTask = 10,
       distributedMemory = True).run()

from biohub.process.apps.annotation import Mlst

Mlst(entity = project,
     threadsPerTask = 10,
     distributedMemory = True).run()

from biohub.process.apps.annotation import ResFinder

ResFinder(entity = project,
          threadsPerTask = 2,
          memoryPerTask = "6GB",
          distributedMemory = True).run()

from biohub.process.apps.annotation import PlasmidFinder

PlasmidFinder(entity = project,
              threadsPerTask = 2,
              memoryPerTask = "6GB",
              distributedMemory = True).run()

from biohub.process.apps.annotation import Rgi

Rgi(entity = project,
    threadsPerTask = 2,
    memoryPerTask = "6GB",
    distributedMemory = True).run()

from biohub.process.apps.align import AlleleCaller
from biohub.process.wrapper import Input

for target in ["multi locus", "aerobactin locus", "colibactin locus", "rmp locus", "salmochelin locus", "yersiniabactin locus", "virulence genes", "wzi locus"]:

    AlleleCaller(entity = project,
                threadsPerTask = 2,
                memoryPerTask = "6GB",
                distributedMemory = True).run(inputs = {"query" : Input(role = "query",
                                                                        biohubFile = database.selectFolder(outlines = {"klebsiella pneumoniae", target})[0],
                                                                        pathPrefix = database.path)},
                                              outputOutlines = {target})

