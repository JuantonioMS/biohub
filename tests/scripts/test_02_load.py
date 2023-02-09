from biohub.utils.creators import EntityCreator
from biohub.process.utils import Load
from biohub.file import File
from biohub.process import Process

from pathlib import Path
from xml.etree import ElementTree as ET
import os

STORAGE_PATH = Path(Path(__file__).parent, "../material/storage")
MATERIAL_PATH = Path(Path(__file__).parent, "../material/files")

def test_subjectLoad():

    subject = EntityCreator().createSubject("subject_test",
                                            f"{STORAGE_PATH}/subjects")

    results = Load(entity = subject).run(inputs = {"_" : Path(MATERIAL_PATH, "a_forward.fq.gz")},
                                         outputOutlines = {"test_output_outline"},
                                         processOutlines = {"test_process_outline"})

    assert isinstance(results, dict)
    assert len(results) == 1

    assert isinstance(subject.files, dict)
    assert len(subject.files) == 1

    fileId, file = list(subject.files.keys())[0], list(subject.files.values())[0]

    assert isinstance(file, File)
    assert "test_output_outline" in file.outlines
    assert "_" not in file.outlines

    assert isinstance(subject.processes, dict)
    assert len(subject.processes) == 1

    processId, process = list(subject.processes.keys())[0], list(subject.processes.values())[0]

    assert isinstance(process, Process)
    assert "test_process_outline" in process.outlines



def test_subjectLinkedLoad():

    subject = EntityCreator().createSubject("subject_test",
                                            f"{STORAGE_PATH}/subjects")

    results = Load(entity = subject).run(inputs = {"_" : Path(MATERIAL_PATH, "a_forward.fq.gz"),
                                                   "aa" : Path(MATERIAL_PATH, "a_reverse.fq.gz")},
                                         outputOutlines = {"test_output_outline"},
                                         processOutlines = {"test_process_outline"})

    assert isinstance(results, dict)
    assert len(results) == 2

    assert isinstance(subject.files, dict)
    assert len(subject.files) == 2

    file1 = list(subject.files.values())[0]
    file2 = list(subject.files.values())[1]

    assert isinstance(file1, File)
    assert "test_output_outline" in file1.outlines
    assert "_" not in file1.outlines
    assert "aa" not in file1.outlines

    assert isinstance(file2, File)
    assert "test_output_outline" in file2.outlines
    assert "aa" in file2.outlines
    assert "_" not in file2.outlines

    assert file1.id in file2.links
    assert file2.id in file1.links

    assert isinstance(subject.processes, dict)
    assert len(subject.processes) == 1

    process = list(subject.processes.values())[0]

    assert isinstance(process, Process)
    assert len(process.inputs) == 2
    assert len(process.outputs) == 2
    assert "test_process_outline" in process.outlines



def test_projectLoad():

    project = EntityCreator().createProject("project_test",
                                            f"{STORAGE_PATH}/projects")

    results = Load(entity = project).run(inputs = {"_" : Path(MATERIAL_PATH, "a_forward.fq.gz")},
                                         outputOutlines = {"test_output_outline"},
                                         processOutlines = {"test_process_outline"})

    assert isinstance(results, dict)
    assert len(results) == 1

    assert isinstance(project.files, dict)
    assert len(project.files) == 1

    fileId, file = list(project.files.keys())[0], list(project.files.values())[0]

    assert isinstance(file, File)
    assert fileId == file.id
    assert "test_output_outline" in file.outlines
    assert "_" not in file.outlines

    assert isinstance(project.processes, dict)
    assert len(project.processes) == 1

    processId, process = list(project.processes.keys())[0], list(project.processes.values())[0]

    assert isinstance(process, Process)
    assert processId == process.id
    assert "test_process_outline" in process.outlines



def test_projectLinkedLoad():

    project = EntityCreator().createProject("project_test",
                                            f"{STORAGE_PATH}/projects")

    results = Load(entity = project).run(inputs = {"_" : Path(MATERIAL_PATH, "a_forward.fq.gz"),
                                                   "aa" : Path(MATERIAL_PATH, "a_reverse.fq.gz")},
                                         outputOutlines = {"test_output_outline"},
                                         processOutlines = {"test_process_outline"})

    assert isinstance(results, dict)
    assert len(results) == 2

    assert isinstance(project.files, dict)
    assert len(project.files) == 2

    file1 = list(project.files.values())[0]
    file2 = list(project.files.values())[1]

    assert isinstance(file1, File)
    assert "test_output_outline" in file1.outlines
    assert "_" not in file1.outlines
    assert "aa" not in file1.outlines

    assert isinstance(file2, File)
    assert "test_output_outline" in file2.outlines
    assert "aa" in file2.outlines
    assert "_" not in file2.outlines

    assert file1.id in file2.links
    assert file2.id in file1.links

    assert isinstance(project.processes, dict)
    assert len(project.processes) == 1

    process = list(project.processes.values())[0]

    assert isinstance(process, Process)
    assert len(process.inputs) == 2
    assert len(process.outputs) == 2
    assert "test_process_outline" in process.outlines

import pytest

@pytest.fixture(autouse = True)
def run_before_and_after_tests(tmpdir):

    yield

    os.system("rm -rf ./test/material/storage/subjects/*")
    os.system("rm -rf ./test/material/storage/projects/*")