from typing import Any

import xml.etree.ElementTree as ET

from biohub.utils import BioHubContainer


class Database(BioHubContainer):


    def addFolder(self, folder): self.addInfoBlock("folders", folder)

    def delFolder(self, folder): self.delInfoBlock("folder", folder)

    def selectFolder(self, **filt) -> list:

        from biohub.folder import Folder

        return [Folder(xmlElement = block) for block in self.selectInfoBlock("folder", **filt)]


    #%%  XML special tags_______________________________________________________________________________________________

    @property
    def _xmlSpecialTags(self) -> set: return {"folders"} | super()._xmlSpecialTags


    #%%  Getters built-in methods_______________________________________________________________________________________


    def __getXmlSpecialTag__(self, attr: str) -> Any:

        if attr == "folders":

            from biohub.file import File
            from biohub.folder import Folder

            aux = {}
            for subelement in self._xml.get(tag = attr)[0]:

                #  Creating an instance with xml info
                instance = locals()[subelement.tag.capitalize()](xmlElement = subelement, entity = self)

                #  Adding to dictionary with id as key, instance as value
                aux[subelement.find("id").text] = instance

            return aux

        else: return super().__getXmlSpecialTag__(attr)



    def __setXmlSpecialTag__(self, attr: str, value: Any) -> None:

        if attr == "folders":

            if getattr(self, attr) is None:
                ET.SubElement(self._xml.root, attr)

        else: super().__setXmlSpecialTag__(attr, value)