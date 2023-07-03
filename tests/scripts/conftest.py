import os
from pathlib import Path
import pytest
import random

STORAGE_PATH = Path(Path(__file__).parent, "../material/storage")


def pytest_configure(config):

    os.system(f"mkdir {STORAGE_PATH}")
    os.system(f"mkdir {STORAGE_PATH}/subjects")
    os.system(f"mkdir {STORAGE_PATH}/projects")
    os.system(f"mkdir {STORAGE_PATH}/databases")

def pytest_unconfigure(config):

    os.system(f"rm -rf {STORAGE_PATH}")


@pytest.fixture(scope = "session")
def MATERIALS_FILES_PATH() -> Path:
    return Path(STORAGE_PATH, "../files")


@pytest.fixture(scope = "session")
def SUBJECTS_PATH() -> Path:
    return Path(STORAGE_PATH, "subjects")


@pytest.fixture(scope = "session")
def PROJECTS_PATH() -> Path:
    return Path(STORAGE_PATH, "projects")


@pytest.fixture(scope = "session")
def DATABASES_PATH() -> Path:
    return Path(STORAGE_PATH, "databases")


@pytest.fixture(scope = "function")
def subject(SUBJECTS_PATH):

    from biohub.utils import EntityCreator

    return EntityCreator().createSubject(f"subject_{random.randint(1,1000):04}",
                                         SUBJECTS_PATH)


@pytest.fixture(scope = "function")
def project(PROJECTS_PATH, subject):

    from biohub.utils import EntityCreator

    return EntityCreator().createProject("project_test",
                                         PROJECTS_PATH,
                                         [subject, subject, subject])