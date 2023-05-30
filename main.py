from biohub.utils import EntityCreator
from biohub.process.apps.utils import Load

import os
from pathlib import Path

os.system("rm -rf ./tests/material/storage/subjects/*")
os.system("rm -rf ./tests/material/storage/projects/*")

subjects = []
for index in range(2):

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

from biohub.process.apps.trimming import Fastp

Fastp(entity = project,
           threadsPerTask = 6,
           concurrentTasks = 2).run()

from biohub.process.apps.taxonomic_profiling import MetaPhlAn

MetaPhlAn(entity = project,
          threadsPerTask = 6,
          concurrentTasks = 2).run()