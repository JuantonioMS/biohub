from datetime import datetime
from xml.etree import ElementTree as ET
from pathlib import Path

from biohub.container import Subject, Project, Database
from biohub.conf.general.constant import ID_PREFIX, ID_LENGTH

def test_subjectCreator(subject, SUBJECTS_PATH):

    #  TYPE
    assert isinstance(subject, Subject)

    #  ID
    assert hasattr(subject, "id")
    assert isinstance(subject.id, str)
    assert ID_PREFIX["Subject"] == subject.id[:len(ID_PREFIX["Subject"])]
    assert len(subject.id) == len(ID_PREFIX["Subject"]) + ID_LENGTH

    #  NAME
    assert hasattr(subject, "name")
    assert isinstance(subject.name, str)
    assert  "subject_" in subject.name
    assert len(subject.name) == 15

    #  DATE
    assert hasattr(subject, "date")
    assert isinstance(subject.date, datetime)
    assert (datetime.now() - subject.date).seconds <= 3

    #  PATH
    assert hasattr(subject, "path")
    assert isinstance(subject.path, Path)
    assert subject.path == Path(SUBJECTS_PATH, f"{subject.id}")

    #  XML METHODS
    assert hasattr(subject, "_xmlElement")
    assert isinstance(subject._xmlElement, ET.Element)
    assert subject._xmlElement.tag == "metadata"
    assert subject._xmlElement.find("name") is not None
    assert subject._xmlElement.find("id") is not None
    assert "date" in subject._xmlElement.attrib

    #  FILES AND FOLDERS
    assert Path(f"{SUBJECTS_PATH}/{subject.id}").is_dir()
    assert Path(f"{SUBJECTS_PATH}/{subject.id}/biohub_subject.xml").is_file()
    assert Path(f"{SUBJECTS_PATH}/{subject.id}/biohub_subject.xml").stat().st_size > 200
    assert Path(f"{SUBJECTS_PATH}/{subject.id}/files").is_dir()



def test_projectCreator(project, PROJECTS_PATH):

    #  TYPE
    assert isinstance(project, Project)

    #  ID
    assert hasattr(project, "id")
    assert isinstance(project.id, str)
    assert ID_PREFIX["Project"] == project.id[:len(ID_PREFIX["Project"])]
    assert len(project.id) == len(ID_PREFIX["Project"]) + ID_LENGTH

    #  NAME
    assert hasattr(project, "name")
    assert isinstance(project.name, str)
    assert len(project.name) == 15

    #  DATE
    assert hasattr(project, "date")
    assert isinstance(project.date, datetime)
    assert (datetime.now() - project.date).seconds <= 3

    #  PATH
    assert hasattr(project, "path")
    assert isinstance(project.path, Path)
    assert project.path == Path(PROJECTS_PATH, f"{project.name}")

    #  SUBJECTS
    assert hasattr(project, "subjects")
    assert isinstance(project.subjects, list)
    assert len(project.subjects) == 3
    assert not any([not isinstance(subject, Subject) for subject in project.subjects])

    #  XML METHODS
    assert hasattr(project, "_xmlElement")
    assert isinstance(project._xmlElement, ET.Element)
    assert project._xmlElement.tag == "metadata"
    assert project._xmlElement.find("name") is not None
    assert project._xmlElement.find("id") is not None
    assert project._xmlElement.find("subjects") is not None
    assert "date" in project._xmlElement.attrib

    #  FILES AND FOLDERS
    assert Path(f"{PROJECTS_PATH}/{project.name}").is_dir()
    assert Path(f"{PROJECTS_PATH}/{project.name}/biohub_project.xml").is_file()
    assert Path(f"{PROJECTS_PATH}/{project.name}/biohub_project.xml").stat().st_size > 200
    assert Path(f"{PROJECTS_PATH}/{project.name}/files").is_dir()