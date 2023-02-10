from typing import Any
from os.path import getsize
from pathlib import Path

from biohub.utils.wrapper import Wrapper


class FileIO(Wrapper):


    @property
    def biohubFile(self) -> Any:

        """Get main object, Path (user management) or File"""

        try: return self._biohubFile
        except AttributeError: return None


    @property
    def path(self) -> Path:

        """Get path to file"""

        if isinstance(self.biohubFile, Path):
            return self.biohubFile

        else:

            try: return Path(self._pathPrefix, self.biohubFile.path)
            except AttributeError: return self.biohubFile.path


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
    def exists(self) -> bool:

        """Get a boolean of the file existence (ej. some/where/file.ext1.ext2 -> False)"""

        return self.path.exists() if isinstance(self.biohubFile, Path) else self.biohubFile.exists


    def __hash__(self) -> int: return hash(self.id)

    def __str__(self) -> str: return self.id

    def __eq__(self, other: object) -> bool:

        try: return self.biohubFile == other.biohubFile

        except (ValueError, AttributeError, TypeError):
            return False



class Input(FileIO):


    @property
    def inputName(self) -> str:

        """Get inputName option if setted, else get str()"""

        try: return self._inputName
        except AttributeError: return ""



    def __str__(self) -> str:
        return f"{self.inputName} {self.path}" if self.inputName else f"{self.path}"



class Output(FileIO):


    @property
    def outputName(self) -> str:

        """Get outputName option if setted, else get str()"""

        try: return self._outputName
        except AttributeError: return ""


    @property
    def temporal(self) -> str:

        """Get temporal output file"""

        try: return self._temporal
        except AttributeError: return None



    def __str__(self) -> str:
        return f"{self.outputName} {self.temporal}" if self.outputName else f"{self.temporal}"