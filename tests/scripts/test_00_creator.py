from biohub.utils.creators import EntityCreator
from datetime import datetime
from pathlib import Path
from xml.etree import ElementTree as ET

import os

STORAGE_PATH = Path(Path(__file__).parent, "../material/storage")

def test_subjectCreator():

    subject = EntityCreator().createSubject("subject_test",
                                            f"{STORAGE_PATH}/subjects")


    assert hasattr(subject, "id")
    assert hasattr(subject, "name")
    assert hasattr(subject, "date")
    assert hasattr(subject, "path")
    assert hasattr(subject, "_xmlElement")

    assert isinstance(subject.name, str)
    assert subject.name == "subject_test"

    assert isinstance(subject.id, str)
    assert subject.id[:4] == "bhSJ"
    assert len(subject.id) == 19

    assert isinstance(subject.date, datetime)
    assert (datetime.now() - subject.date).seconds <= 3

    assert isinstance(subject.path, Path)
    assert subject.path == Path(STORAGE_PATH, f"subjects/{subject.id}")

    assert isinstance(subject._xmlElement, ET.Element)
    assert subject._xmlElement.tag == "metadata"
    assert subject._xmlElement.find("name") is not None
    assert subject._xmlElement.find("id") is not None
    assert "date" in subject._xmlElement.attrib

    assert Path(f"{STORAGE_PATH}/subjects/{subject.id}").is_dir()
    assert Path(f"{STORAGE_PATH}/subjects/{subject.id}/biohub_subject.xml").is_file()
    assert Path(f"{STORAGE_PATH}/subjects/{subject.id}/biohub_subject.xml").stat().st_size > 200
    assert Path(f"{STORAGE_PATH}/subjects/{subject.id}/files").is_dir()



def test_projectCreator():

    project = EntityCreator().createProject("project_test",
                                            f"{STORAGE_PATH}/projects")

    assert hasattr(project, "id")
    assert hasattr(project, "name")
    assert hasattr(project, "date")
    assert hasattr(project, "path")
    assert hasattr(project, "_xmlElement")

    assert isinstance(project.name, str)
    assert project.name == "project_test"

    assert isinstance(project.id, str)
    assert project.id[:4] == "bhPJ"
    assert len(project.id) == 19

    assert isinstance(project.date, datetime)
    assert (datetime.now() - project.date).seconds <= 3

    assert isinstance(project.path, Path)
    assert project.path == Path(STORAGE_PATH, f"projects/{project.name}")

    assert isinstance(project._xmlElement, ET.Element)
    assert project._xmlElement.tag == "metadata"
    assert project._xmlElement.find("name") is not None
    assert project._xmlElement.find("id") is not None
    assert "date" in project._xmlElement.attrib

    assert Path(f"{STORAGE_PATH}/projects/{project.name}").is_dir()
    assert Path(f"{STORAGE_PATH}/projects/{project.name}/biohub_project.xml").is_file()
    assert Path(f"{STORAGE_PATH}/projects/{project.name}/biohub_project.xml").stat().st_size > 200
    assert Path(f"{STORAGE_PATH}/projects/{project.name}/files").is_dir()

import pytest

@pytest.fixture(autouse = True)
def run_before_and_after_tests(tmpdir):

    yield

    os.system("rm -rf ./test/material/storage/subjects/*")
    os.system("rm -rf ./test/material/storage/projects/*")