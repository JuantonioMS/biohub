from os.path import getsize

from typing import Any

from pathlib import Path

from xml.etree import ElementTree as ET

from biohub.utils import BioHubClass

class File(BioHubClass):

    def __init__(self,
                 xmlElement: ET.Element = ET.Element("file"),
                 **attrs) -> None:

        super().__init__(xmlElement, **attrs)


    def newId(self):

        return "bhFL" + super().newId()

    @property
    def _xmlElementTags(self) -> set: return {"links"} | super()._xmlElementTags

    @property
    def _xmlSpecialTags(self) -> set: return {"path"} | super()._xmlSpecialTags



    def __getXmlSpecialTag__(self, attr: str) -> Any:

        if attr == "path":

            element = self._xmlElement.find(attr)

            if element is not None:
                return Path(element.text)

            else:
                return None

        else: return super().__getXmlSpecialTag__(attr)



    def __setXmlSpecialTag__(self, attr: str, value: Any) -> None:

        if attr == "path":

            if getattr(self, attr) is not None:
                self._xmlElement.remove(attr)

            subelement = ET.SubElement(self._xmlElement, attr)
            subelement.text = str(value)

        else: return super().__setXmlSpecialTag__(attr, value)




    #  Getters__________________________________________________________________________________________________________


    @property
    def file(self) -> str:

        """Get the full name of the file (ej. some/where/file.ext1.ext2 -> file.ext1.ext2)"""

        return self.path.name


    @property
    def stem(self) -> str:

        """Get only the stem of the file (ej. some/where/file.ext1.ext2 -> file)"""

        return self.file[:-len(self.suffixes)]


    @property
    def suffixes(self) -> str:

        """Get only the suffixes of the file (ej. some/where/file.ext1.ext2 -> .ext1.ext2)"""

        return "".join(self.path.suffixes)


    @property
    def parent(self) -> str:

        """Get only the path to the file (ej. some/where/file.ext1.ext2 -> some/where)"""

        return self.path.parent


    @property
    def size(self) -> int:

        """Get file size (ej. some/where/file.ext1.ext2 -> 65)
        If file does not exist return 0
        """

        return getsize(self.path) if self.exists else 0


    @property
    def exists(self) -> bool:

        """Get a boolean of the file existence (ej. some/where/file.ext1.ext2 -> False)"""

        return self.path.exists()


    #  _________________________Magic Methods_________________________


    def __eq__(self, other: object) -> bool:

        return self.id == other.id