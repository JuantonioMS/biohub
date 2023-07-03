from pathlib import Path
import pytest

from biohub.process.apps.utils import Load

@pytest.fixture(scope = "function")
def subject(subject, MATERIALS_FILES_PATH):

    Load(entity = subject).run(inputs = {"forward" : Path(MATERIALS_FILES_PATH, "illumina_reads_paired_forward.fq"),
                                         "reverse" : Path(MATERIALS_FILES_PATH, "illumina_reads_paired_reverse.fq")},
                               outputOutlines = {"illumina", "reads", "short", "raw", "paired"})

    return subject