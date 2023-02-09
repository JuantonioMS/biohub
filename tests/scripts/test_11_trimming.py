from biohub.utils.creators import EntityCreator
from biohub.process.utils import Load

from pathlib import Path

STORAGE_PATH = Path(Path(__file__).parent, "../material/storage")
MATERIAL_PATH = Path(Path(__file__).parent, "../material/files")


subject = EntityCreator().createSubject("subject_test",
                                        f"{STORAGE_PATH}/subjects")

Load(entity = subject).run(inputs = {"forward" : Path(MATERIAL_PATH, "a_forward.fq.gz"),
                                        "reverse" : Path(MATERIAL_PATH, "a_reverse.fq.gz")},
                           outputOutlines = {"reads", "raw"})

def test_pairedTrimgalore():

    subject = EntityCreator().createSubject("subject_test",
                                            f"{STORAGE_PATH}/subjects")

    Load(entity = subject).run(inputs = {"forward" : Path(MATERIAL_PATH, "a_forward.fq.gz"),
                                            "reverse" : Path(MATERIAL_PATH, "a_reverse.fq.gz")},
                               outputOutlines = {"reads", "raw"})

    from biohub.process.trimming import Trimgalore

    results = Trimgalore(entity = subject, threads = 4, save = True).run()

    assert results



def test_pairedBayesHammer():

    subject = EntityCreator().createSubject("subject_test",
                                            f"{STORAGE_PATH}/subjects")

    Load(entity = subject).run(inputs = {"forward" : Path(MATERIAL_PATH, "a_forward.fq.gz"),
                                            "reverse" : Path(MATERIAL_PATH, "a_reverse.fq.gz")},
                               outputOutlines = {"reads", "raw"})

    from biohub.process.trimming import BayesHammer

    results = BayesHammer(entity = subject, threads = 4, save = True).run()

    assert results