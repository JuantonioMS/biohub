from pathlib import Path
import pytest

from biohub.process.apps.utils import Load

@pytest.fixture(scope = "function")
def subject(subject, MATERIALS_FILES_PATH):

    Load(entity = subject).run(inputs = {"genome" : Path(MATERIALS_FILES_PATH, "illumina_assembly.fasta")},
                               outputOutlines = {"illumina", "assembly"})

    return subject


@pytest.fixture(scope = "function")
def project(project, MATERIALS_FILES_PATH):

    for subject in project.subjects:

        Load(entity = subject).run(inputs = {"genome" : Path(MATERIALS_FILES_PATH, "illumina_assembly.fasta")},
                                   outputOutlines = {"illumina", "assembly"})

    return project