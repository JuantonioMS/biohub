from typing import Any

from biohub.utils import BioHubContainer
from biohub.subject import Subject


class Project(BioHubContainer):

    def newId(self):
        return "bhPJ" + super().newId()


    def __getattribute__(self, attr: str) -> Any:

        if attr in "subjects":


            aux = []
            for subelement in self._xml.get(tag = attr)[0]:

                instance = Subject(path = f"{self.path}/../../subjects/{subelement.text}/biohub_subject.xml")

                aux.append(instance)

            return aux

        else:
            return super().__getattribute__(attr)