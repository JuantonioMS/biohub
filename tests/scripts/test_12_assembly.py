from biohub.utils.creators import EntityCreator
from biohub.process.utils import Load

from pathlib import Path

STORAGE_PATH = Path(Path(__file__).parent, "../material/storage")
MATERIAL_PATH = Path(Path(__file__).parent, "../material/files")

def test_pairedUnicyler():

    subject = EntityCreator().createSubject("subject_test",
                                            f"{STORAGE_PATH}/subjects")

    Load(entity = subject).run(inputs = {"forward" : Path(MATERIAL_PATH, "a_forward.fq.gz"),
                                            "reverse" : Path(MATERIAL_PATH, "a_reverse.fq.gz")},
                            outputOutlines = {"reads", "raw"})

    from biohub.process.trimming import Trimgalore

    Trimgalore(entity = subject, threads = 4).run()

    from biohub.process.assembly import Unicycler

    results = Unicycler(entity = subject, threads = 4).run()

    assert results
