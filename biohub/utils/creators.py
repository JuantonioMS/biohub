from pathlib import Path
import subprocess

from biohub.utils import verifyPath

from biohub.utils import BioHubClass

from datetime import datetime

import random

CHARACTERS = "0123456789qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM"
NCHARS = 15

class EntityCreator:


    def verifyName(self, name):

        aux = ""
        for char in name:

            if char in [".", ",", " ", "-"]:
                aux += "_"

            else: aux += char

        return aux



    def createSubject(self,
                      name: str,
                      path: Path):

        from biohub.subject import Subject

        from xml.etree import ElementTree as ET
        from xml.dom import minidom

        newName = name

        newId = "bhSJ" + "".join(random.choices(CHARACTERS, k = NCHARS))

        subprocess.call(f"mkdir {verifyPath(path)}/{newId}",
                        shell = True,
                        executable = "/bin/bash")
        subprocess.call(f"touch {verifyPath(path)}/{newId}/biohub_subject.xml",
                        shell = True,
                        executable = "/bin/bash")

        subject = ET.Element("subject")
        metadata = ET.SubElement(subject, "metadata")

        metadata.attrib["date"] = datetime.now().strftime("%Y/%b/%d %H:%M:%S")

        name = ET.SubElement(metadata, "name")
        name.text = self.verifyName(newName)

        bhId = ET.SubElement(metadata, "id")
        bhId.text = newId

        for case in ["files", "processes", "pipelines"]:
            _ = ET.SubElement(subject, case)


        prettyXml = minidom.parseString(ET.tostring(subject)\
                                        .decode("UTF-8").replace("\n", "")\
                                        .replace("    ", ""))\
                                        .toprettyxml(indent = "    ")


        with open(f"{verifyPath(path)}/{newId}/biohub_subject.xml", "wb") as biohubFile:
            biohubFile.write(prettyXml.encode("utf-8"))

        subject = Subject(path = f"{verifyPath(path)}/{newId}/biohub_subject.xml")

        return subject



    def createProject(self,
                      name: str,
                      path: Path,
                      subjects: list = []):

        from biohub.project import Project

        from xml.etree import ElementTree as ET
        from xml.dom import minidom

        newName = name

        newId = "bhPJ" + "".join(random.choices(CHARACTERS, k = NCHARS))

        subprocess.call(f"mkdir {verifyPath(path)}/{newName}",
                        shell = True,
                        executable = "/bin/bash")
        subprocess.call(f"touch {verifyPath(path)}/{newName}/biohub_project.xml",
                        shell = True,
                        executable = "/bin/bash")

        project = ET.Element("project")
        metadata = ET.SubElement(project, "metadata")

        metadata.attrib["date"] = datetime.now().strftime("%Y/%b/%d %H:%M:%S")

        name = ET.SubElement(metadata, "name")
        name.text = self.verifyName(newName)

        bhId = ET.SubElement(metadata, "id")
        bhId.text = newId

        subjectsElement = ET.SubElement(metadata, "subjects")
        for subject in subjects:
            subjectElement = ET.SubElement(subjectsElement, "subject")
            subjectElement.text = f"{subject}"

        for case in ["files", "processes", "pipelines"]:
            _ = ET.SubElement(project, case)

        prettyXml = minidom.parseString(ET.tostring(project)\
                                        .decode("UTF-8").replace("\n", "")\
                                        .replace("    ", ""))\
                                        .toprettyxml(indent = "    ")


        with open(f"{verifyPath(path)}/{newName}/biohub_project.xml", "wb") as biohubFile:
            biohubFile.write(prettyXml.encode("utf-8"))

        project = Project(path = f"{verifyPath(path)}/{newName}/biohub_project.xml")

        return project