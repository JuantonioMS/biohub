from typing import Any

from biohub.utils import BioHubContainer


class Project(BioHubContainer):

    #%%  XML special tags_______________________________________________________________________________________________


    @property
    def _xmlSpecialTags(self) -> set:
        return {"subjects"} | super()._xmlSpecialTags


    #%%  Getters built-in methods_______________________________________________________________________________________


    def __getXmlSpecialTag__(self, attr: str) -> Any:

        if attr == "subjects":

            from biohub.subject import Subject

            aux, warning = [], []
            for subelement in self._xml.get(tag = attr)[0]:

                try:
                    instance = Subject(path = f"{self.path}/../../subjects/{subelement.text}/biohub_subject.xml")
                    aux.append(instance)

                except: warning.append(subelement.text)

            if warning: print(f"!!!WARNING!!! {len(warning)} subjects could not be loaded ids: {warning}")

            return aux

        else: return super().__getXmlSpecialTag__(attr)



    #%%  Setters built-in methods_______________________________________________________________________________________


    def __setXmlSpecialTag__(self, attr: str, value: Any) -> None:

        if attr == "subjects":

            from biohub.subject import Subject


            from xml.etree import ElementTree as ET


            if not self.subjects:

                subjects = self._xml.root.find("subjects")

                for subject in value:

                    if isinstance(subject, Subject):
                        ET.SubElement(subjects, subject.id)

                    elif isinstance(subject, str):
                        ET.SubElement(subjects, subject)

        else: super().__setXmlSpecialTag__(attr, value)