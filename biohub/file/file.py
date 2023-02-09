from os.path import getsize

from biohub.utils import BioHubClass

class File(BioHubClass):


    def newId(self):

        return "bhFL" + super().newId()


    #  Getters__________________________________________________________________________________________________________


    @property
    def specialAttrs(self) -> set:
        return super().specialAttrs.union({"path", "links"})


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