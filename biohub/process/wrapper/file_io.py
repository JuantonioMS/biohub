from typing import Union, Any
from os.path import getsize
from pathlib import Path

from biohub.storage import File

from biohub.process.wrapper import Wrapper

DEFAULT_FILE = "file.txt"
DEFAULT_EXTENSION = ".txt"


class FileIO(Wrapper):

    @property
    def biohubFile(self) -> Any:

        """Get main object, Path (user management) or File"""

        try: return self._biohubFile
        except AttributeError: return None


    @biohubFile.setter
    def biohubFile(self, value: Union[Path, File]) -> None:

        self._biohubFile = value


    @property
    def path(self) -> Path:

        """Get path to file"""

        if isinstance(self.biohubFile, Path):
            return self.biohubFile

        else:

            try: return Path(self.pathPrefix, self.biohubFile.path)
            except AttributeError: return self.biohubFile.path


    @property
    def pathPrefix(self) -> Path:

        try: return self._pathPrefix
        except AttributeError: return Path()


    @pathPrefix.setter
    def pathPrefix(self, value: Path) -> Path:
        self._pathPrefix = Path(value)


    @property
    def id(self) -> str:

        """Get biohubFile id, if Path get str of path"""

        return str(self.path) if isinstance(self.biohubFile, Path) else self.biohubFile.id


    @property
    def file(self) -> str:

        """Get the full name of the file (ej. some/where/file.ext1.ext2 -> file.ext1.ext2)"""

        return self.biohubFile.name if isinstance(self.biohubFile, Path) else self.biohubFile.file


    @property
    def suffixes(self) -> str:

        """Get only the suffixes of the file (ej. some/where/file.ext1.ext2 -> .ext1.ext2)"""

        return "".join(self.biohubFile.suffixes) if isinstance(self.biohubFile, Path) else self.biohubFile.suffixes


    @property
    def stem(self) -> str:

        """Get only the stem of the file (ej. some/where/file.ext1.ext2 -> file)"""

        return self.file[:-len(self.suffixes)] if isinstance(self.biohubFile, Path) else self.biohubFile.stem


    @property
    def parent(self) -> Path:

        """Get only the path to the file (ej. some/where/file.ext1.ext2 -> some/where)"""

        return self.biohubFile.parent if isinstance(self.biohubFile, Path) else self.biohubFile.parent


    @property
    def size(self) -> int:

        """Get file size (ej. some/where/file.ext1.ext2 -> 65)
        If file does not exist return 0
        """

        if isinstance(self.biohubFile, Path):
            return getsize(self.path) if self.exists else 0

        else:
            return self.biohubFile.size


    @property
    def evalAttributes(self) -> set:
        return {"name"} | super().evalAttributes


    @property
    def name(self):

        try: return self._name
        except AttributeError: return ""


    @property
    def exists(self) -> bool:

        """Get a boolean of the file existence (ej. some/where/file.ext1.ext2 -> False)"""

        return self.path.exists() if isinstance(self.biohubFile, Path) else self.biohubFile.exists



    def __hash__(self) -> int: return hash(self.id)



    def __str__(self) -> str:
        msg = self.format

        if self.name: msg = msg.replace("<name>", self.name)
        else: msg = msg.replace("<name>", "")

        return msg



    def __eq__(self, other: object) -> bool:

        try: return self.biohubFile == other.biohubFile

        except (ValueError, AttributeError, TypeError):
            return False



class Input(FileIO):

    @property
    def selection(self):
        try: return self._selection
        except AttributeError: return []


    def __str__(self) -> str:

        msg = super().__str__().replace("<value>", str(self.path))

        return msg.strip()



class Output(FileIO):

    @property
    def evalAttributes(self) -> set:
        return {"extension", "temporal"} | super().evalAttributes


    @property
    def temporal(self) -> str:

        """Get temporal output file"""

        try: return self._temporal
        except AttributeError: return DEFAULT_FILE

    @temporal.setter
    def temporal(self, value: str) -> None:
        self._temporal = value


    @property
    def outlines(self) -> set:

        try: return self._outlines
        except AttributeError: return set()


    @outlines.setter
    def outlines(self, value: set) -> None:

        self._outlines = value


    @property
    def extension(self) -> str:

        try: return self._extension
        except AttributeError: return DEFAULT_EXTENSION


    @extension.setter
    def extension(self, value: str) -> None:
        self._extension = value


    def __str__(self) -> str:

        msg = super().__str__().replace("<value>", str(self.temporal))

        return msg.strip()
